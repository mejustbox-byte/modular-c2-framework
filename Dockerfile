FROM python:3.12.14-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 TMPDIR=/run/lab
WORKDIR /app
COPY mocklab /app/mocklab
COPY integration /app/integration
USER 10001:10001
CMD ["python", "-m", "mocklab.server"]
