FROM python:3.9-slim as builder
RUN apt-get update && \
    apt-get install -y gnupg2 build-essential && \
    python3.9 -m pip install update
COPY requirements.txt requirements.txt
RUN python3.9 -m pip install -r requirements.txt

FROM python:3.9-slim
COPY --from=builder /usr/local/lib/python3.9/ /usr/local/lib/python3.9/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
WORKDIR /app
COPY start.py /app/start.py
COPY src/ /app/src/
COPY cleanup.sh /usr/local/bin/
CMD ["cleanup.sh"]