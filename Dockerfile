FROM python:3.9-alpine as builder
RUN apk update && \
    apk --no-cache --update add build-base && \
    python3.9 -m pip install update
COPY requirements.txt requirements.txt
RUN python3.9 -m pip install -r requirements.txt

FROM python:3.9-alpine
COPY --from=builder /usr/local/lib/python3.9/ /usr/local/lib/python3.9/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
WORKDIR /app
COPY start.py /app/start.py
COPY src/ /app/src/
COPY cleanup.sh /usr/local/bin/
CMD ["cleanup.sh"]