from kraken_api import *
from settings import PAIRS

if __name__ == "__main__":
    server_time = get_server_time()["rfc1123"]
    system_status = get_system_status()
    print(f"Hello, server is {system_status['status']} and time is", server_time)

    pairs = get_asset_pairs(pairs_list=PAIRS)
    print("Selected pairs: ")
    for pair in pairs:
        print(pair)
    # print(get_ticker_information(pair="XETHXXBT"))
    # print(get_account_balance())
    # print(get_trade_balance("ZUSD"))
    # print(get_open_orders())
    # print(get_closed_orders())
    # print(get_orders_info(txid_list=["1"]))

    # print(get_asset_pairs(["USDCGBP"]))
    # print(get_account_balance())
    # print(get_ticker_information(pair="USDCGBP"))
    # print(
    #     add_order(
    #         order_type="limit",
    #         type="buy",
    #         volume=0.0001,
    #         pair="BTCGBP",
    #         price=1,
    #         start_time=datetime.datetime.now() + datetime.timedelta(seconds=5),
    #         expiration_time=datetime.datetime.now() + datetime.timedelta(minutes=2),
    #         validate=True,
    #     )
    # )
