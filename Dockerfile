# -------- base OS layer (small) -------------------
FROM python:3.13-slim

# -------- system dependencies ----------------------
RUN apt-get update \
    && apt-get install -y wget gnupg ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Add Google Chrome signing key and repo
RUN wget -qO- https://dl.google.com/linux/linux_signing_key.pub \
    | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list

# Install Chrome + Chromedriver
RUN apt-get update \
    && apt-get install -y google-chrome-stable chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# -------- python dependencies ---------------------
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -------- application code -------------------------
COPY . .

# -------- runtime environment ----------------------
ENV PYTHONUNBUFFERED=1 \
    CHROME_BIN=/usr/bin/google-chrome \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver \
    FLASK_APP=run:app \
    FLASK_ENV=production

EXPOSE 8000

# Run migrations then start the application
CMD ["sh", "-c", "flask db upgrade && exec gunicorn -b 0.0.0.0:${PORT:-8000} run:app"]    