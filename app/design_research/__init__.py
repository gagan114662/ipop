"""Design Research Module.

This module handles visual research and aesthetic intelligence:
- scrapers: Behance, Pinterest, Dribbble, Instagram Ad Library
- analyzers: Vision model integration for aesthetic analysis
- training: Taste model training from human feedback
- synthesis: Prompt engineering for creative generation
"""

from . import scrapers
from . import analyzers
from . import training
from . import synthesis
from . import models

__all__ = ["scrapers", "analyzers", "training", "synthesis", "models"]
