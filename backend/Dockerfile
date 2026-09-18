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
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN groupadd --gid 1000 rola && useradd --uid 1000 --gid rola --create-home rola
COPY --from=builder /wheels /wheels
RUN python -m pip install --no-cache-dir /wheels/* && rm -rf /wheels
COPY manage.py ./
RUN mkdir -p media static /storage/media /storage/static && chown -R rola:rola /app /storage
USER rola
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "rola.wsgi:application"]
