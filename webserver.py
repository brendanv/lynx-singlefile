import subprocess
import logging
from flask import Flask, request, Response
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', force=True)
logger = logging.getLogger(__name__)

server = Flask(__name__)

SINGLEFILE_EXECUTABLE = './single-file'
BROWSER_PATH = '/usr/bin/chromium-browser'
BROWSER_ARGS = '["--no-sandbox"]'


@server.route('/', methods=['POST'])
def singlefile():
    url = request.form.get('url')
    cookies = request.form.get('cookies')
    parsed_cookies = (json.loads(cookies) if cookies else None) or []
    if url:
        logger.info('Received request for URL: %s (cookies: %d)', url, len(parsed_cookies))
        args = [
            "node",
            SINGLEFILE_EXECUTABLE,
            '--browser-executable-path=' + BROWSER_PATH,
            "--browser-args='%s'" % BROWSER_ARGS,
            '--browser-wait-until=loaded',
            request.form['url'],
            '--dump-content',
        ]
        if parsed_cookies:
            for parsed_cookie in parsed_cookies:
              args.extend(['--browser-cookie', parsed_cookie])

        logger.info('Spawning single-file process')
        p = subprocess.Popen(
            args,
            stdout=subprocess.PIPE)
    else:
        logger.warning('Request received with no URL parameter')
        return Response('Error: url parameter not found.',
                        status=500)
    singlefile_html = p.stdout.read()
    p.terminate()
    logger.info('Finished processing %s (%d bytes)', url, len(singlefile_html))
    return Response(
        singlefile_html,
        mimetype="text/html",
    )


if __name__ == '__main__':
    server.run(host='0.0.0.0', port=80)
