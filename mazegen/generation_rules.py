"""Instance-owned constraints for maze generation and pattern placement."""


class GenerationRules:
    """Keep rule values on each instance, not in shared constants."""

    def __init__(self) -> None:
        """Initialize the fixed constraints for this generation session."""
        self.max_generation_attempts = 30
        self.min_independent_cycles = 2
        self.max_dead_ends = 2
        self.forbidden_open_area_size = 3
