import base64
import datetime
import hashlib
import hmac
import httpx
import urllib.parse

from settings import API_KEY, BASE_URL, CONTENT_TYPE, BASE_DOMAIN, SECRET_API_KEY


class KrakenException(Exception):
    pass


def get_nonce() -> int:
    return int(datetime.datetime.now().timestamp())


def get_kraken_signature(url: str, data: dict) -> str:
    urlpath = url.split(BASE_DOMAIN)[1]
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data["nonce"]) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    mac = hmac.new(base64.b64decode(SECRET_API_KEY), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()


def kraken_get_request(url: str, params: dict = None) -> dict:
    response = httpx.get(url, params=params)
    # TODO catch HTTP errors
    data = response.json()
    if len(data["error"]) > 0:
        error_message = data["error"][0]
        raise KrakenException(error_message)
    return data["result"]


def kraken_post_request(url: str, *, data: dict = {}) -> dict:
    data["nonce"] = get_nonce()
    headers = {"Content-Type": CONTENT_TYPE, "API-Key": API_KEY, "API-Sign": get_kraken_signature(url, data)}
    response = httpx.post(url, data=data, headers=headers)
    # TODO catch HTTP errors
    data = response.json()
    if len(data["error"]) > 0:
        raise KrakenException(data["error"][0])
    return data["result"]


# PUBLIC ENDPOINTS


def get_server_time() -> dict:
    url = f"{BASE_URL}public/Time"
    return kraken_get_request(url)


def get_system_status() -> dict:
    url = f"{BASE_URL}public/SystemStatus"
    return kraken_get_request(url)


def get_assets(assets_list: "list[str]", aclass: str = None) -> dict:
    url = f"{BASE_URL}public/Assets"
    asset = ",".join(assets_list)
    params = dict(asset=asset)
    if aclass is not None:
        params["aclass"] = aclass
    return kraken_get_request(url, params=params)


def get_asset_pairs(pairs_list: "list[str]" = [], info: str = None) -> dict:
    url = f"{BASE_URL}public/AssetPairs"
    params = {}
    if len(pairs_list) > 0:
        pair = ",".join(pairs_list)
        params["pair"] = pair
    if info is not None:
        params["info"] = info
    return kraken_get_request(url, params=params)


def get_ticker_information(pair: str) -> dict:
    url = f"{BASE_URL}public/Ticker"
    params = dict(pair=pair)
    return kraken_get_request(url, params=params)


# PRIVATE ENDPOINTS


def get_account_balance() -> dict:
    url = f"{BASE_URL}private/Balance"
    return kraken_post_request(url)


def get_trade_balance(asset: str) -> dict:
    url = f"{BASE_URL}private/TradeBalance"
    return kraken_post_request(url, data={"asset": asset})


def get_open_orders(trades: bool = True) -> dict:
    url = f"{BASE_URL}private/OpenOrders"
    trades = "true" if trades else "false"
    return kraken_post_request(url, data={"trades": trades})


def get_closed_orders(
    trades: bool = True,
    start: datetime.datetime = datetime.datetime.now() - datetime.timedelta(days=300),
    end: datetime.datetime = datetime.datetime.now(),
) -> dict:
    url = f"{BASE_URL}private/ClosedOrders"
    trades = "true" if trades else "false"
    data = {"trades": trades, "start": int(start.timestamp()), "end": int(end.timestamp())}
    return kraken_post_request(url, data=data)


def get_orders_info(trades: bool = True, txid_list: "list[str]" = []) -> dict:
    url = f"{BASE_URL}private/QueryOrders"
    trades = "true" if trades else "false"
    data = {"trades": trades}
    if len(txid_list) > 0:
        data["txid"] = ",".join(txid_list)
    return kraken_post_request(url, data=data)


#### DANGER ZONE


def add_order(
    *,
    order_type: str,
    type: str,
    volume: float,
    pair: str,
    start_time: datetime.datetime,
    expiration_time: datetime.datetime,
    validate: bool = True,
    price: float = None,
    always_yes: bool = False,
):
    url = f"{BASE_URL}private/AddOrder"

    if order_type not in ["market", "limit"]:
        raise Exception("order_type should be either 'market' or 'limit'")

    if type not in ["buy", "sell"]:
        raise Exception("type must be one of 'buy' or 'sell'")

    if order_type == "limit" and price is None:
        raise Exception("price must be specified if order_type is limit")

    if start_time < datetime.datetime.now():
        raise Exception(f"Order start time is in the past: {start_time}")

    if expiration_time < start_time:
        raise Exception(f"Expiration time is before start time: {expiration_time} < {start_time}")

    data = {
        "ordertype": order_type,
        "type": type,
        "volume": str(volume),
        "pair": pair,
        "starttm": int(start_time.timestamp()),
        "expiretm": int(expiration_time.timestamp()),
        "validate": "true" if validate else "false",
    }

    if price is not None:
        data["price"] = price

    if not always_yes:
        proceed = input(
            f"Please confirm that you wish to execute order {type} {volume} {pair} @ {order_type} {price if order_type == 'limit' else ''} [y/N] "
        )
    else:
        proceed = "y"

    if proceed == "y":
        return kraken_post_request(url, data=data)
    else:
        print("Order not issued.")
        return {}
