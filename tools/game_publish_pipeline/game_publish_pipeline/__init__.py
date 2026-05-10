"""Higher-order orchestration for game obfuscation followed by deployment."""

from .pipeline import build_parser, run_pipeline

__all__ = ["build_parser", "run_pipeline"]