"""Menu text constructed locally for interaction and terminal sizing."""


def main_menu() -> tuple[tuple[str, ...], str]:
    """Return menu choices and their prompt."""
    options = (
        "1. Re-generate maze",
        "2. Show/Hide shortest path",
        "3. Change maze wall colors",
        "4. Change solution path color",
        "5. Change 42 pattern color",
        "6. Exit",
    )
    return options, "Choice (1-6): "


def regeneration_menu() -> tuple[tuple[str, ...], str]:
    """Return regeneration choices without shared module data."""
    options = (
        "1. Generate a new maze",
        "2. Regenerate using a seed",
    )
    return options, "Choice (1-2): "
