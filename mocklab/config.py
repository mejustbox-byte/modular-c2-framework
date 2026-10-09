"""Strict bounded TOML configuration for the offline exercise, not network policy."""

import tomllib
from dataclasses import dataclass

from .core import LabError, identifier


@dataclass(frozen=True)
class Config:
    lab_id: str = "synthetic-lab"
    max_events: int = 1000
    max_requests: int = 1000
    burst: int = 100

    @classmethod
    def parse(cls, content):
        if type(content) is not bytes or len(content) > 4096:
            raise LabError("invalid_config")
        try:
            data = tomllib.loads(content.decode("utf-8"))
        except (ValueError, UnicodeError, RecursionError):
            raise LabError("invalid_config") from None
        if data.keys() - {"lab_id", "max_events", "max_requests", "burst"}:
            raise LabError("unknown_config_field")
        config = cls(**data)
        identifier(config.lab_id)
        for limit in (config.max_events, config.max_requests):
            if type(limit) is not int or not 2 <= limit <= 10000:
                raise LabError("invalid_limit")
        if type(config.burst) is not int or not 1 <= config.burst <= 1000:
            raise LabError("invalid_limit")
        return config
