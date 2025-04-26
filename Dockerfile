# -------- base OS layer (very small) -------------------
    FROM python:3.12-slim

    # -------- system deps ----------------------------------
    RUN apt-get update && apt-get install -y wget gnupg ca-certificates

    # add Google signing key
    RUN wget -qO- https://dl.google.com/linux/linux_signing_key.pub \
        | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg
    
    # add the repo
    RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] \
            http://dl.google.com/linux/chrome/deb/ stable main" \
            > /etc/apt/sources.list.d/google-chrome.list
    
    # install Chrome + any other packages you need
    RUN apt-get update && apt-get install -y google-chrome-stable chromium-driver \
        && rm -rf /var/lib/apt/lists/*
    
    # -------- python deps ----------------------------------
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    
    # -------- app code -------------------------------------
    COPY . .
    
    # -------- runtime setup --------------------------------
    ENV PYTHONUNBUFFERED=1 \
        CHROME_BIN=/usr/bin/google-chrome \
        CHROMEDRIVER_PATH=/usr/bin/chromedriver
    
    EXPOSE 8000
    CMD ["gunicorn", "-b", "0.0.0.0:8000", "run:app"]