"""Generation constraints required by the maze specification."""

# Retries bound the search for a braided layout satisfying every constraint.
MAX_GENERATION_ATTEMPTS = 30
MIN_INDEPENDENT_CYCLES = 2
MAX_DEAD_ENDS = 2
# Larger completely open rooms are forbidden; inspect their shared walls.
FORBIDDEN_OPEN_AREA_SIZE = 3
