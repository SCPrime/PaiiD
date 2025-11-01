"""DEX Meme Scout strategy configuration."""

from __future__ import annotations

from pydantic import BaseModel, Field


class DexMemeScoutConfig(BaseModel):
    """Configuration for DEX meme coin scouting."""

    name: str = "DEX Meme Scout"
    tokens: list[str] = Field(
        default_factory=lambda: ["pepe", "bonk", "weth", "usdc", "shib"],
        description="List of token symbols to monitor",
    )
    max_new_positions: int = 3
    allocation_usd: float = 250.0
    max_positions: int = 6
    min_change_pct: float = 8.0
    momentum_window_minutes: int = 60


class DexMemeScoutStrategy:
    """Placeholder strategy class for DEX Meme Scout metrics."""

    def __init__(self, config: DexMemeScoutConfig):
        self.config = config


def create_dex_meme_scout_strategy(
    config_dict: dict | None = None,
) -> DexMemeScoutStrategy:
    config = DexMemeScoutConfig(**config_dict) if config_dict else DexMemeScoutConfig()
    return DexMemeScoutStrategy(config)


__all__ = [
    "DexMemeScoutConfig",
    "DexMemeScoutStrategy",
    "create_dex_meme_scout_strategy",
]
