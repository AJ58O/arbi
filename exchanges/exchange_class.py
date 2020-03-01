#Defines the methods that every exchange API needs to include
import exchanges.wallets
import json

class Exchange:
	def __init__(self, exchange_name, authed_exchange):
		self.e = authed_exchange
		self.name = exchange_name
		self.fees = authed_exchange.fees
		with open('exchanges/wallets/{0}.json'.format(exchange_name)) as wallet_file:
			self.wallet = json.load(wallet_file)

	def get_buy_price(self, market):
		return float(self.e.get_buy_price(market))

	def get_sell_price(self, market):
		return float(self.e.get_sell_price(market))

	def buy(self, market, amount, price, order_type=None, addtl_params={}):
		return self.e.buy(market, amount, price, order_type=order_type, addtl_params=addtl_params)

	def sell(self, market, amount, price, order_type=None, addtl_params={}):
		return self.e.sell(market, amount, price, order_type=order_type, addtl_params=addtl_params)

	def send_tx(self, currency, quantity, address, memo=None):
		return self.e.send_tx(currency, quantity, address, memo)

	def get_balance(self, currency):
		return float(self.e.get_balance(currency))

	def order_complete(self, orderId, market):
		return bool(self.e.order_complete(orderId, market))

	def get_open_orders(self, market):
		return self.e.get_open_orders(market)

	def cancel(self, market, orderId):
		return self.e.cancel(market, orderId)
