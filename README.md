# Crypto Trading Bot

Using Kraken REST API

## Usage

Create environment with (requires python3.8 and python3.8-venv):

```
python3.8 -m venv env
./env/bin/pip install --upgrade pip
./env/bin/pip install -r requrements.in
```

Run with

```
./env/bin/python src/main.py
```

## API documentation

### Request Headers and Responses

Always set `User-Agent` and `Content-Type: application/x-www-form-urlencoded`.

Response examples:

```
{
  "error": [],
  "result": {
    "status": "online",
    "timestamp": "2021-03-22T17:18:03Z"
  }
}
```

```
{
  "error": [
    "EGeneral:Invalid arguments:ordertype"
  ]
}
```
Status codes are always 200, unless there was a client or server error.

Authenticated requests must include both `API-Key` and `API-Sign` HTTP headers, and `nonce` in the request payload. `nonce` is an always increasing integer for each request made with a specific API key, e.g. unix timestamp. `API-Sign` should be:

```
HMAC-SHA512 of (URI path + SHA256(nonce + POST data)) and base64 decoded secret API key
```

For example:
```python
def get_kraken_signature(urlpath, data, secret):

    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()
```

### Rate Limits

Every user gets an API Counter that increases by 2 every history call and by 1 every other call. It decreases by 0.5 every second, and the limit is 20.

That translates roughly to 20 call warm up and then 0.5 call/second or 30 calls/minute.

There are different, more complicated rules for the number of open orders on each asset at a time.