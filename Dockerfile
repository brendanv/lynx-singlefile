FROM zenika/alpine-chrome:with-node

USER root
RUN apk add --no-cache python3 py3-pip

RUN npm install --production single-file-cli

WORKDIR /usr/src/app/node_modules/single-file-cli

COPY requirements.txt .
RUN pip install \ 
  --no-cache-dir \ 
  --no-warn-script-location \
  --user \
  --break-system-packages \
  -r requirements.txt \
  && rm requirements.txt

COPY webserver.py .

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python3 -c "import sys,urllib.request; sys.exit(0 if urllib.request.urlopen('http://localhost:80/health', timeout=3).status == 200 else 1)"

ENTRYPOINT [ \
    "node", \
    "./single-file", \
    "--browser-executable-path", "/usr/bin/chromium-browser", \
    "--output-directory", "./../../out/", \
    "--browser-args", "[\"--no-sandbox\"]", \
    "--dump-content" ]