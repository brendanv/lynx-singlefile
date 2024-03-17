import subprocess
from flask import Flask, request, Response
import json

server = Flask(__name__)

SINGLEFILE_EXECUTABLE = './single-file'
BROWSER_PATH = '/usr/bin/chromium-browser'
BROWSER_ARGS = '["--no-sandbox"]'


@server.route('/', methods=['POST'])
def singlefile():
    url = request.form.get('url')
    cookies = request.form.get('cookies')
    parsed_cookies = json.loads(cookies) if cookies else []
    if url:
        args = [
            "node",
            SINGLEFILE_EXECUTABLE,
            '--browser-executable-path=' + BROWSER_PATH,
            "--browser-args='%s'" % BROWSER_ARGS,
            request.form['url'],
            '--dump-content',
        ]
        if parsed_cookies:
            for parsed_cookie in parsed_cookies:
              args.extend(['--browser-cookie', parsed_cookie])
  
        p = subprocess.Popen(
            args,
            stdout=subprocess.PIPE)
    else:
        return Response('Error: url parameter not found.',
                        status=500)
    singlefile_html = p.stdout.read()
    p.terminate()
    return Response(
        singlefile_html,
        mimetype="text/html",
    )


if __name__ == '__main__':
    server.run(host='0.0.0.0', port=80)
