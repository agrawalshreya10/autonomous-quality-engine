"""Test helpers: data generation, date utils, selector labels for logs, etc."""

import random
import string
from datetime import datetime


def truncate_for_log(text: str, max_len: int = 100) -> str:
    """Shorten long selectors/URLs for log lines."""
    t = text.strip()
    if len(t) <= max_len:
        return t
    return f"{t[: max_len - 3]}..."


def random_string(length: int = 8, prefix: str = "") -> str:
    """Return a random alphanumeric string, optionally with prefix."""
    chars = string.ascii_lowercase + string.digits
    suffix = "".join(random.choices(chars, k=length))
    return f"{prefix}{suffix}" if prefix else suffix


def unique_employee_name() -> tuple[str, str]:
    """Return (first_name, last_name) with timestamp for uniqueness."""
    base = datetime.now().strftime("%m%d%H%M")
    return f"Test{base}", f"User{base}"
