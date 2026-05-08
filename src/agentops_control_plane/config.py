"""Runtime configuration for the AgentOps Control Plane."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Application settings sourced from environment variables."""

    database_path: Path = Path("agentops_demo.sqlite3")

    @classmethod
    def from_env(cls) -> Settings:
        return cls(database_path=Path(os.getenv("AGENTOPS_DATABASE_PATH", "agentops_demo.sqlite3")))
