FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

COPY requirements.txt .

# pywin32 Windows-only hai, Docker Linux hai
RUN grep -v '^pywin32==' requirements.txt > /tmp/requirements-docker.txt \
    && pip install \
        --default-timeout=300 \
        --retries=20 \
        --no-cache-dir \
        -r /tmp/requirements-docker.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "frontend.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]