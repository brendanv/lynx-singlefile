# Lynx-Singlefile
This is a dockerized wrapper of [Singlefile](https://github.com/gildas-lormeau/SingleFile) that allows you to create standalone archives of webpages by calling into a http service. It is intended to be used alonside [Lynx](https://github.com/brendanv/lynx), a self-hostable read-it-later app.

> [!NOTE]
> This is a forked version of [Singlefile-dockerized](https://github.com/screenbreak/SingleFile-dockerized) which is in turn a wrapper around [single-file-cli](https://github.com/gildas-lormeau/single-file-cli). Take a look at the documentation for those projects to see how it all fits together.
> The only thing this project adds on to those is the ability to pass in cookies for creating archives of pages behind a login.

## Suggested Usage

Run this container using a docker-compose.yaml file similar to this: 

```yaml
version: '3'
services:
  singlefile:
    container_name: singlefile
    image: ghcr.io/brendanv/lynx-singlefile
    entrypoint: python3
    command: webserver.py
    expose:
      - 80
```

Then any HTTP POST on port 80 with url parameter will respond with the HTML output of SingleFile in the payload:

```bash
curl -d 'url=http://www.example.com/' singlefile:80
```

### Providing Cookies
If you want to create an archive of pages that are behind a login, this image supports a cookies parameter that will be passed along when loading your page.

The cookie parameter expects a _JSON-encoded list of strings_ where each string represents a single cookie. Each individual cookie string must be a comma-separated list of the cookie's (name, value, domain, path, expires, httpOnly, secure, sameSite, url). The first three parameters are required but the rest are optional.

Some python pseudocode:

```python
import json
import requests

cookie = ','.join(['cookie-name', 'cookie-value', 'domain'])
cookies = json.dumps([cookie])
requests.post('singlefile:80', data={'url': url, 'cookies': cookies})
```