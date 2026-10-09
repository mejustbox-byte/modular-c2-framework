FROM python:3.12.15-alpine3.24@sha256:1b668429b3511ab407d8e00648891631b0b1a4d7e15e3ca70f38ab5b91ad4ab4
RUN apk add --no-cache zlib=1.3.2-r1 \
    && python -m pip uninstall -y pip \
    && rm -rf /usr/local/lib/python3.12/ensurepip
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 TMPDIR=/run/lab
WORKDIR /app
COPY mocklab /app/mocklab
COPY integration /app/integration
USER 10001:10001
CMD ["python", "-m", "mocklab.server"]
