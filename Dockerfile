FROM gcc:latest AS builder
RUN wget http://download.redis.io/redis-stable.tar.gz && \
    tar xvzf redis-stable.tar.gz && \
    cd redis-stable && make
FROM python:3.12-slim
WORKDIR /spam

COPY --from=builder /redis-stable/src/redis-server /usr/local/bin/
COPY --from=builder /redis-stable/src/redis-cli /usr/local/bin/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY run.sh /run.sh
RUN chmod +x /run.sh

EXPOSE 8000 6379
ENTRYPOINT ["/run.sh"]
