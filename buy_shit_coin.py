import ccxt
import json


class Param:
    def __init__(self, param: dict):
        # Quote currency (XXX/USDT   <--)
        self.quote = param["quote"]
        # Quote currency amount
        self.investment_amount = param["investment_amount"]
        # If price under "bar" then buy.
        self.bar = param["bar"]
        # Quantity to buy at a time (quote currency base.) ex: 1 USDT
        self.lot = param["lot"]


class Strategy:
    def __init__(self, api_key: str, api_secret: str, param_path: str = "./param.json"):
        self.binance = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
        })
        self.param_path = param_path
        config_open = open(self.param_path, "r")
        param_json = json.load(config_open)
        self.param = Param(param_json)
        self.investment_amount = min(self.param.investment_amount, self.get_balance())

    def script(self):
        tickers = self.binance.fetch_tickers()
        new_tickers = sorted(tickers.items(), key=lambda x: x[1]["last"])
        for symbol in new_tickers:
            if f"/{self.param.quote}" in symbol[0]:
                price = tickers[symbol[0]]["last"]
                if price <= self.param.bar:
                    if self.investment_amount > self.param.lot:
                        buy_num = int(self.param.lot / price)
                        try:
                            order_result = self.binance.create_market_buy_order(
                                symbol=symbol[0],
                                amount=buy_num
                            )
                            if "status" in order_result and order_result["status"] == "FILLED":
                                self.investment_amount -= float(order_result["cummulativeQuoteQty"])
                                print(f"Bought {buy_num} {symbol[0].split('/')[0]}")
                        except Exception as e:
                            print(e)

    def get_balance(self):
        return self.binance.fetch_balance()[self.param.quote]["free"]


def main():
    config_open = open("./param.json", "r")
    param_json = json.load(config_open)

    strategy = Strategy(
        api_key=param_json["api_key"],
        api_secret=param_json["api_secret"]
    )

    strategy.script()


if __name__ == '__main__':
    main()
