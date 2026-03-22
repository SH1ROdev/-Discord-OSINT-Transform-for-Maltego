FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    curl \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

ENTRYPOINT ["python", "project.py"]

CMD []