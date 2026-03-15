import os

OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL: str = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
MAX_HISTORY_LENGTH: int = int(os.environ.get("MAX_HISTORY_LENGTH", "10"))

if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY environment variable is not set. "
        "Please set it before starting the application."
    )
