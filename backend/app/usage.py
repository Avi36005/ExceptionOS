"""Token usage tracking helpers."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    provider: str = ""
    model: str = ""

    def add(self, other: "TokenUsage") -> None:
        self.prompt_tokens += other.prompt_tokens
        self.completion_tokens += other.completion_tokens
        self.total_tokens += other.total_tokens

    def to_dict(self) -> dict[str, Any]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "provider": self.provider,
            "model": self.model,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "TokenUsage":
        return cls(
            prompt_tokens=d.get("prompt_tokens", 0),
            completion_tokens=d.get("completion_tokens", 0),
            total_tokens=d.get("total_tokens", 0),
            provider=d.get("provider", ""),
            model=d.get("model", ""),
        )


@dataclass
class AggregatedUsage:
    runs: list[TokenUsage] = field(default_factory=list)

    def add(self, usage: TokenUsage) -> None:
        self.runs.append(usage)

    @property
    def totals(self) -> dict[str, int]:
        return {
            "prompt_tokens": sum(r.prompt_tokens for r in self.runs),
            "completion_tokens": sum(r.completion_tokens for r in self.runs),
            "total_tokens": sum(r.total_tokens for r in self.runs),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            **self.totals,
            "by_provider": {
                r.provider: r.to_dict() for r in self.runs if r.provider
            },
        }
