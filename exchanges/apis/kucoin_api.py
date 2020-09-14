import os
import json
from kucoin.client import Client

class kucoin_api:
	def __init__(self, key, secret, passphrase):
		self.client = Client(key, secret, passphrase)
		self.fees = .0025

	def get_buy_price(self, market):
		return self.client.get_order_book(market)["bids"][0][0]

	def get_sell_price(self, market):
		return self.client.get_order_book(market)["asks"][0][0]

	def buy(self, market, amount, price, order_type=None, addtl_params={}):
		currency = market.split("-")[1]
		balance = self.get_withdraw_balance(currency)
		if float(balance) > 0:
			move = self.move_from_withdraw_to_trade(currency, balance)
		buy = self.client.create_limit_order(market, Client.SIDE_BUY, price, amount)
		try:
			return buy["orderId"]
		except:
			print("except")
			print(buy)
			return buy

	def stop_buy(self, market, amount, price, stop_price):
		currency = market.split("-")[1]
		balance = self.get_withdraw_balance(currency)
		if float(balance) > 0:
			move = self.move_from_withdraw_to_trade(currency, balance)
		buy = self.client.create_limit_order(market, Client.SIDE_BUY, price, amount, stop="entry", stop_price=stop_price)
		try:
			return buy["orderId"]
		except:
			print("except")
			print(buy)
			return buy


	def sell(self, market, amount, price, order_type=None, addtl_params={}):
		currency = market.split("-")[0]
		balance = self.get_withdraw_balance(currency)
		if float(balance) > 0:
			move = self.move_from_withdraw_to_trade(currency, balance)
			print(move)
		sell = self.client.create_limit_order(market, Client.SIDE_SELL, price, amount)
		try:
			return sell["orderId"]
		except:
			print("except")
			print(sell)
			return sell

	def stop_sell(self, market, amount, price, stop_price):
		currency = market.split("-")[0]
		balance = self.get_withdraw_balance(currency)
		if float(balance) > 0:
			move = self.move_from_withdraw_to_trade(currency, balance)
			print(move)
		sell = self.client.create_limit_order(market, Client.SIDE_SELL, price, amount, stop="loss", stop_price=stop_price)
		try:
			return sell["orderId"]
		except:
			print("except")
			print(sell)
			return sell

	def send_tx(self, currency, quantity, address, memo):
		balance = self.get_trading_balance(currency)
		print(balance)
		if float(balance) > 0:
			move = self.move_from_trade_to_withdraw(currency, balance)
		if currency == "USDT":
			if address[0] == "T":
				return self.client.create_withdrawal(currency, quantity, address, memo=memo, chain="TRC20")	
			else:
				return self.client.create_withdrawal(currency, quantity, address, memo=memo, chain="ERC20")	
		return self.client.create_withdrawal(currency, quantity, address, memo=memo)

	def get_balance(self, currency):
		return sum([float(cur["available"]) for cur in self.client.get_accounts() if cur["currency"] == currency])

	def get_withdraw_balance(self, currency):
		return [cur["available"] for cur in self.client.get_accounts() if cur["currency"] == currency and cur["type"] == "main"][0]

	def get_trading_balance(self, currency):
		return [cur["available"] for cur in self.client.get_accounts() if cur["currency"] == currency and cur["type"] == "trade"][0]

	def order_complete(self, orderId, market=None):
		return not bool(self.client.get_order(orderId)["isActive"])

	def get_deposit_address(self, currency):
		return self.client.get_deposit_address(currency)

	def move_from_trade_to_withdraw(self, currency, amount):
		cur_accounts = [cur for cur in self.client.get_accounts() if cur["currency"] == currency]
		main = [account for account in cur_accounts if account["type"] == "main"][0]
		trade = [account for account in cur_accounts if account["type"] == "trade"][0]
		return self.client.create_inner_transfer(trade["id"], main["id"], amount)

	def move_from_withdraw_to_trade(self, currency, amount):
		cur_accounts = [cur for cur in self.client.get_accounts() if cur["currency"] == currency]
		main = [account for account in cur_accounts if account["type"] == "main"][0]
		trade = [account for account in cur_accounts if account["type"] == "trade"][0]
		return self.client.create_inner_transfer(main["id"], trade["id"], amount)		

	def get_orders(self, symbol=None, status=None, side=None):
		return self.client.get_orders(symbol=symbol, status=status, side=side)

	def get_open_orders(self, symbol):
		return self.get_orders(symbol=symbol, status="active")

	def cancel(self, symbol, orderId):
		return self.client.cancel_order(orderId)


# k = kucoin_api(os.environ["KUCOIN_KEY"], os.environ["KUCOIN_SECRET"], os.environ["KUCOIN_PASSPHRASE"])
# market = "XRP-USDT"

# print(json.dumps(k.get_orders(symbol=market, side="buy")))


# # print(k.buy("XRP-USDT", 5, .25))

# print(k.get_trading_balance("XRP"))
# print(k.get_withdraw_balance("XRP"))
# print(k.move_from_withdraw_to_trade("XRP", 1))
# print((k.client.get_deposit_address("USDT")))
# print(k.client.create_deposit_address("USDT", chain="ERC20"))