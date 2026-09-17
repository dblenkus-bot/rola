FROM python:3.14.7-slim AS builder
WORKDIR /build
COPY . .
RUN python -m pip wheel --no-cache-dir --wheel-dir /wheels .

FROM python:3.14.7-slim AS development
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN python -m pip install --no-cache-dir /wheels/* && rm -rf /wheels
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

FROM python:3.14.7-slim AS production
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    ROLA_MEDIA_ROOT=/storage/media ROLA_STATIC_ROOT=/storage/static
WORKDIR /app
RUN groupadd --gid 1000 rola && useradd --uid 1000 --gid rola --create-home rola
COPY --from=builder /wheels /wheels
RUN python -m pip install --no-cache-dir /wheels/* && rm -rf /wheels
COPY manage.py ./
RUN mkdir -p /storage/media /storage/static && chown -R rola:rola /app /storage
USER rola
EXPOSE 8000
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "rola.asgi:application"]
