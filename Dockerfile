FROM zenika/alpine-chrome

USER root
RUN apk add --no-cache nodejs npm python3 py3-pip \
    && npm install --production single-file-cli \
    && npm cache clean --force \
    && apk del npm

WORKDIR /usr/src/app/node_modules/single-file-cli

COPY requirements.txt .
RUN pip install \
  --no-cache-dir \
  --no-warn-script-location \
  --break-system-packages \
  -r requirements.txt \
  && rm requirements.txt

COPY webserver.py .

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python3 -c "import sys,urllib.request; sys.exit(0 if urllib.request.urlopen('http://localhost:80/health', timeout=3).status == 200 else 1)"

ENTRYPOINT ["gunicorn", "-w", "1", "-b", "0.0.0.0:80", "webserver:server"]
