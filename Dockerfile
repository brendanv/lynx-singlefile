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

ENTRYPOINT [ \
    "node", \
    "./single-file", \
    "--browser-executable-path", "/usr/bin/chromium-browser", \
    "--output-directory", "./../../out/", \
    "--browser-args", "[\"--no-sandbox\"]", \
    "--dump-content" ]