FROM python:3.12.15-slim-bookworm@sha256:34386ef0cb081344d7ec1c103ba398e6e9f64e9ab3a1509accc92a4e24a07258
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 TMPDIR=/run/lab
WORKDIR /app
COPY mocklab /app/mocklab
COPY integration /app/integration
USER 10001:10001
CMD ["python", "-m", "mocklab.server"]
