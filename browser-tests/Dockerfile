FROM mcr.microsoft.com/playwright/python:v1.63.0-noble@sha256:72bd171a9ffc2b4b59532aaa6210e21014d07093120dc25528870c0b840da1f0
RUN apt-get update && apt-get install -y --no-install-recommends libnss3-tools openssl && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir playwright==1.63.0
ENV HOME=/run/lab TMPDIR=/run/lab XDG_CACHE_HOME=/run/lab/cache MOZ_CRASHREPORTER_DISABLE=1
COPY test_browser.py /app/test_browser.py
USER 10001:10001
CMD ["python", "/app/test_browser.py"]
