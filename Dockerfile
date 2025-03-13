# Используем официальный образ Playwright на Python
FROM mcr.microsoft.com/playwright/python:v1.49.1-noble

RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    fonts-liberation \
    libxcb-shm0 \
    xvfb\
    && apt-get clean

ENV PYTHONUNBUFFERED=1
ENV TG_API_TOKEN=7520872258:AAHxy0EHiZJAjDmeDU05bdNv9YnnoDf0HKc
ENV DATABASE_URL=sqlite+aiosqlite:///database.db
WORKDIR /app

RUN python -m pip install --upgrade pip
RUN pip install playwright==1.40.0
RUN playwright install chromium

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN chmod -R a+x /usr/local/lib/python3.12/dist-packages/undetected_playwright/driver

COPY . /app

CMD ["bash", "-c", "xvfb-run -a python -u tg_bot.py 2>&1"]
