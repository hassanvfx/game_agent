FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    git \
    gnupg \
    npm \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libatspi2.0-0 \
    libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt \
    && python -m playwright install chromium

RUN npm install -g @cline/cli

COPY app /app/app
COPY tools /app/tools

ENV CELERY_BROKER_URL=redis://redis:6379/0 \
    CELERY_RESULT_BACKEND=redis://redis:6379/1 \
    CELERY_TASK_DELAY_SECONDS=2 \
    LOG_LEVEL=INFO \
    PLAYWRIGHT_HEADLESS=true \
    PLAYWRIGHT_BROWSER=chromium \
    CLINE_CHECK_COMMAND="clite --help"

CMD ["celery", "-A", "app.tasks", "worker", "--loglevel=INFO"]