import logging
import os
import signal
import subprocess
from flask import Flask, request, Response
import json

server = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

SINGLEFILE_EXECUTABLE = './single-file'
BROWSER_PATH = '/usr/bin/chromium-browser'
BROWSER_ARGS = '["--no-sandbox"]'
# A hung Chromium process used to wedge the entire (single-threaded) server
# forever, since reads from the subprocess had no timeout. Bound it.
REQUEST_TIMEOUT_SECONDS = int(os.environ.get('SINGLEFILE_TIMEOUT_SECONDS', '90'))


@server.route('/health', methods=['GET'])
def health():
    return Response('OK', status=200)


@server.route('/', methods=['POST'])
def singlefile():
    url = request.form.get('url')
    if not url:
        server.logger.warning('Request missing url parameter')
        return Response('Error: url parameter not found.', status=500)

    cookies = request.form.get('cookies')
    parsed_cookies = json.loads(cookies) if cookies else []

    server.logger.info('Archiving %s (cookies: %d)', url, len(parsed_cookies))

    args = [
        "node",
        SINGLEFILE_EXECUTABLE,
        '--browser-executable-path=' + BROWSER_PATH,
        "--browser-args='%s'" % BROWSER_ARGS,
        url,
        '--dump-content',
    ]
    if parsed_cookies:
        for parsed_cookie in parsed_cookies:
            args.extend(['--browser-cookie', parsed_cookie])

    # New session/process group so a timeout can kill the whole tree
    # (node + the chromium it launches), not just the node process.
    p = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    try:
        singlefile_html, stderr = p.communicate(timeout=REQUEST_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        p.communicate()
        server.logger.error('Timed out archiving %s after %ds', url, REQUEST_TIMEOUT_SECONDS)
        return Response(
            'Error: timed out generating archive for %s' % url, status=504)

    if p.returncode != 0:
        server.logger.error(
            'single-file failed for %s (exit %s): %s',
            url, p.returncode, stderr.decode(errors='replace'))
        return Response('Error: single-file process failed.', status=500)

    server.logger.info('Archived %s (%d bytes)', url, len(singlefile_html))
    return Response(singlefile_html, mimetype="text/html")


if __name__ == '__main__':
    server.run(host='0.0.0.0', port=80)
