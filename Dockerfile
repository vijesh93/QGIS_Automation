FROM qgis/qgis:latest

# Build-time proxy args
ARG http_proxy
ARG https_proxy

# Set environment proxies for the OS
ENV http_proxy=$http_proxy
ENV https_proxy=$https_proxy

WORKDIR /app

# Install system packages and python venv support
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install requirements inside a virtual environment to avoid PEP 668 errors
COPY requirements.txt .
# Create venv that can see system site-packages (so QGIS and PyQt5 are available)
RUN python3 -m venv /opt/venv --system-site-packages \
    && /opt/venv/bin/pip install --upgrade pip setuptools wheel \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Ensure the venv's python is used for subsequent steps and at runtime
ENV PATH="/opt/venv/bin:$PATH"

# Making sure Python can find QGIS' python modules (some images put them here)
ENV PYTHONPATH="/usr/share/qgis/python:$PYTHONPATH"

# ... (Build args and additional build steps can follow) ...

# 1. Copy the code into the image for Production use
COPY . /app

# 2. Set the default command (Production default)
CMD ["python3", "test/test_db_connection.py"]
