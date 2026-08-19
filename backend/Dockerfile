FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# PyTorch somente CPU — evita baixar CUDA/NVIDIA
RUN pip install --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu \
    torch==2.3.1

# Demais dependências
RUN pip install --no-cache-dir --prefer-binary \
    -r requirements.txt

COPY app ./app
COPY scripts ./scripts

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]