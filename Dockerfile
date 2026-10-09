FROM python:3.12.14-slim-bookworm@sha256:392307d22300de8b5986851a12d9176dfc0fc073e65bf6523ebd7dcbeb23564e
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 TMPDIR=/run/lab
WORKDIR /app
COPY mocklab /app/mocklab
COPY integration /app/integration
USER 10001:10001
CMD ["python", "-m", "mocklab.server"]
