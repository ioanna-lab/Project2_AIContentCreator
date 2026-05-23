"""
LLM Integration — OpenAI API wrapper with cost tracking.

Single provider (OpenAI) for Week 1 MVP. Designed to be extended
to multi-provider in Week 2 if needed.

Includes rate limiting, token counting, and cost tracking so every
content generation request is accounted for.
"""
import time
import logging
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("llm_integration")

# ── Pricing (USD per million tokens) ─────────────────────────────────────────
PRICING = {
    "gpt-4o-mini": {"input": 0.15,  "output": 0.60},
    "gpt-4o":      {"input": 2.50,  "output": 10.00},
}

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def count_tokens_approx(text: str) -> int:
    """
    Approximate token count using the 4-chars-per-token heuristic.
    Good enough for cost estimation without importing tiktoken.
    """
    return len(text) // 4


class CostTracker:
    """Track cumulative API spend across all calls in a session."""

    def __init__(self):
        self.total_cost = 0.0
        self.requests   = []

    def track(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Record one request and return its cost in USD."""
        pricing     = PRICING.get(model, {"input": 3.0, "output": 15.0})
        input_cost  = (input_tokens  / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        cost        = input_cost + output_cost

        self.total_cost += cost
        self.requests.append({
            "model":         model,
            "input_tokens":  input_tokens,
            "output_tokens": output_tokens,
            "cost":          cost,
        })
        logger.debug(
            "Cost: model=%s in=%d out=%d cost=$%.6f total=$%.4f",
            model, input_tokens, output_tokens, cost, self.total_cost
        )
        return cost

    def summary(self) -> dict:
        """Return a summary dict of all requests."""
        return {
            "total_requests":  len(self.requests),
            "total_cost":      self.total_cost,
            "total_tokens":    sum(r["input_tokens"] + r["output_tokens"] for r in self.requests),
            "average_cost":    self.total_cost / max(len(self.requests), 1),
        }


class LLMClient:
    """
    OpenAI client wrapper with rate limiting and cost tracking.

    Designed for easy extension: add ask_anthropic() or ask_with_fallback()
    in Week 2 without changing any calling code.
    """

    def __init__(self, model: str = DEFAULT_MODEL):
        self.client      = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model       = model
        self.cost_tracker = CostTracker()
        self.last_call   = 0
        # gpt-4o-mini: 500 RPM free tier → ~0.12s minimum interval
        self.min_interval = 0.12

        logger.info("LLMClient initialised with model '%s'", self.model)

    def _rate_limit(self):
        """Pause if we are calling too fast."""
        elapsed = time.time() - self.last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_call = time.time()

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1500,
    ) -> str:
        """
        Send a system + user prompt to OpenAI and return the response text.

        Args:
            system_prompt: Sets the behaviour and persona for this call
            user_prompt:   The specific content request
            temperature:   Creativity level (0=deterministic, 1=creative)
            max_tokens:    Maximum response length

        Returns:
            Response text string

        Raises:
            Exception: on API error
        """
        self._rate_limit()

        input_tokens = count_tokens_approx(system_prompt + user_prompt)
        logger.debug(
            "OpenAI request: model=%s ~%d input tokens", self.model, input_tokens
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        output_text   = response.choices[0].message.content.strip()
        output_tokens = count_tokens_approx(output_text)

        cost = self.cost_tracker.track(self.model, input_tokens, output_tokens)
        logger.info(
            "Generated %d chars (~%d tokens) for $%.6f",
            len(output_text), output_tokens, cost
        )

        return output_text

    def print_cost_summary(self):
        """Print a formatted cost summary to stdout."""
        s = self.cost_tracker.summary()
        print(f"\n{'='*50}")
        print(f"COST SUMMARY")
        print(f"{'='*50}")
        print(f"Requests:      {s['total_requests']}")
        print(f"Total tokens:  {s['total_tokens']:,}")
        print(f"Total cost:    ${s['total_cost']:.4f}")
        print(f"Avg per req:   ${s['average_cost']:.6f}")
        print(f"{'='*50}")


# ── Quick smoke test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s | %(levelname)-8s | %(message)s")

    client = LLMClient()
    response = client.generate(
        system_prompt="You are a helpful assistant.",
        user_prompt="What is prompt engineering? Answer in two sentences.",
    )
    print(f"\nResponse: {response}")
    client.print_cost_summary()
