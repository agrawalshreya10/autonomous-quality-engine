# Failure-Aware Test Framework (FATF) — Phase 1 smoke runner
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

# Unprivileged runtime user (CWE-250): pytest + Chromium must not run as root
RUN useradd --create-home --shell /usr/sbin/nologin fatf
COPY --chown=fatf:fatf . .

# pytest-html / screenshots expect this tree; fatf needs /app write + browser read/exec
RUN mkdir -p reports/screenshots \
    && chown -R fatf:fatf /app \
    && chmod -R a+rX /ms-playwright

# Defaults match public demo when unset (config/settings.py); override via `docker run -e`
# Do not set ORANGEHRM_PASSWORD here.
ENV BROWSER=chromium \
    HEADLESS=true

USER fatf

# Override args as needed, e.g. docker run ... fatf-smoke pytest -m smoke -n auto
CMD ["pytest", "-m", "smoke", "-v", "--tb=short", \
     "--html=reports/report.html", "--self-contained-html"]
