FROM apache/airflow:2.7.1

USER root

# Linux paket listesini güncelle ve gerekli bağımlılıkları kur
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    unzip \
    libgconf-2-4 \
    libnss3 \
    libxss1 \
    libasound2 \
    xvfb \
    libxi6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# --- DÜZELTME: Chrome 149'un Google sunucularındaki aktif tam sürümünü çekiyoruz ---
RUN wget -q "https://storage.googleapis.com/chrome-for-testing-public/149.0.7827.197/linux64/chrome-linux64.zip" && \
    unzip chrome-linux64.zip && \
    mv chrome-linux64 /opt/google-chrome && \
    ln -s /opt/google-chrome/chrome /usr/bin/google-chrome && \
    rm -rf chrome-linux64.zip

# --- DÜZELTME: Chrome ile birebir uyumlu 149 ChromeDriver'ı indirip sabitliyoruz ---
RUN wget -q "https://storage.googleapis.com/chrome-for-testing-public/149.0.7827.197/linux64/chromedriver-linux64.zip" && \
    unzip chromedriver-linux64.zip && \
    mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf chromedriver-linux64.zip chromedriver-linux64

USER airflow

# Kütüphaneleri bağlıyoruz
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.7.1/constraints-3.8.txt"