# Autonomous Quality Engine — Phase 1 smoke runner
# Python 3.12 + Playwright Chromium for `pytest -m smoke`.
# Pass BASE_URL / ORANGEHRM_* (and related) as env at runtime — never bake secrets in.

FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    # Playwright browsers live inside the image (not host .playwright-browsers)
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    HEADLESS=true

WORKDIR /app

# System libs for Chromium (Playwright --with-deps); keep layer cacheable with requirements first
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && playwright install --with-deps chromium

COPY . .

# pytest-html / screenshots expect this tree
RUN mkdir -p reports/screenshots

# Defaults match public demo when unset (config/settings.py); override via `docker run -e`
# Do not set ORANGEHRM_PASSWORD here.
ENV BROWSER=chromium \
    HEADLESS=true

# Override args as needed, e.g. docker run ... aqe-smoke pytest -m smoke -n auto
CMD ["pytest", "-m", "smoke", "-v", "--tb=short", \
     "--html=reports/report.html", "--self-contained-html"]
