"""Shared menu text used by the application and terminal size calculations."""

MENU_OPTIONS = (
    "1. Re-generate maze",
    "2. Show/Hide shortest path",
    "3. Change maze wall colors",
    "4. Change solution path color",
    "5. Change 42 pattern color",
    "6. Exit",
)
MENU_PROMPT = "Choice (1-6): "
INVALID_CHOICE_MESSAGE = "Please enter a number from 1 to 6."

REGENERATION_OPTIONS = (
    "1. Generate a new maze",
    "2. Regenerate using a seed",
)
REGENERATION_PROMPT = "Choice (1-2): "
INVALID_REGENERATION_MESSAGE = "Please enter a number from 1 to 2."
SEED_PROMPT = "Seed [{seed}] (Enter to keep current): "
