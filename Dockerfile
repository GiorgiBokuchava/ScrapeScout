# ---------- base image -------------------------------------------------------
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends wget gnupg ca-certificates unzip \
    && rm -rf /var/lib/apt/lists/*

# ---------- Google Chrome ----------------------------------------------------
RUN wget -qO- https://dl.google.com/linux/linux_signing_key.pub \
    | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] \
    http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list

RUN apt-get update \
    && apt-get install -y --no-install-recommends google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# ---------- matching ChromeDriver (Chrome-for-Testing bucket) ----------------
RUN set -eux; \
    CHROME_FULL="$(google-chrome --version | awk '{print $3}')"; \
    DRIVER_ZIP_URL="https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROME_FULL}/linux64/chromedriver-linux64.zip"; \
    echo "Fetching driver for Chrome $CHROME_FULL …"; \
    wget -qO /tmp/chromedriver.zip "$DRIVER_ZIP_URL"; \
    # extract only the executable, strip directory (-j)                     ↓ path inside zip
    unzip -q -j /tmp/chromedriver.zip chromedriver-linux64/chromedriver -d /usr/local/bin/; \
    rm /tmp/chromedriver.zip; \
    chmod +x /usr/local/bin/chromedriver; \
    chromedriver --version

# ---------- Python dependencies ---------------------------------------------
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- application code -------------------------------------------------
COPY . .

ENV PYTHONUNBUFFERED=1 \
    CHROME_BIN=/usr/bin/google-chrome \
    CHROMEDRIVER_PATH=/usr/local/bin/chromedriver \
    FLASK_APP=run:app \
    FLASK_ENV=production \
    PORT=8000

EXPOSE ${PORT}

CMD ["sh", "-c", "flask db upgrade && exec gunicorn -b 0.0.0.0:${PORT} run:app"]
