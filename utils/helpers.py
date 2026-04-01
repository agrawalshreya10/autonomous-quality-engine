"""Test helpers: data generation, date utils, etc."""

import random
import string
from datetime import datetime, timedelta


def random_string(length: int = 8, prefix: str = "") -> str:
    """Return a random alphanumeric string, optionally with prefix."""
    chars = string.ascii_lowercase + string.digits
    suffix = "".join(random.choices(chars, k=length))
    return f"{prefix}{suffix}" if prefix else suffix


def unique_employee_name() -> tuple[str, str]:
    """Return (first_name, last_name) with timestamp for uniqueness."""
    base = datetime.now().strftime("%m%d%H%M")
    return f"Test{base}", f"User{base}"
