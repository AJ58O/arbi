#Defines the methods that every exchange API needs to include
import exchanges.wallets
import json
import time

class Exchange:
	def __init__(self, exchange_name, authed_exchange):
		self.e = authed_exchange
		self.name = exchange_name
		self.fees = authed_exchange.fees
		self.time_out = 2
		with open('exchanges/wallets/{0}.json'.format(exchange_name)) as wallet_file:
			self.wallet = json.load(wallet_file)

	def get_buy_price(self, market):
		try:
			return float(self.e.get_buy_price(market))
		except:
			time.sleep(self.time_out)
			return float(self.e.get_buy_price(market))

	def get_sell_price(self, market):
		try:
			return float(self.e.get_sell_price(market))
		except:
			time.sleep(self.time_out)
			return float(self.e.get_sell_price(market))


	def buy(self, market, amount, price, order_type=None, addtl_params={}):
		try:
			return self.e.buy(market, amount, price, order_type=order_type, addtl_params=addtl_params)
		except:
			time.sleep(self.time_out)
			return self.e.buy(market, amount, price, order_type=order_type, addtl_params=addtl_params)

	def sell(self, market, amount, price, order_type=None, addtl_params={}):
		try:
			return self.e.sell(market, amount, price, order_type=order_type, addtl_params=addtl_params)
		except:
			time.sleep(self.time_out)
			return self.e.sell(market, amount, price, order_type=order_type, addtl_params=addtl_params)

	def send_tx(self, currency, quantity, address, memo=None):
		try:
			return self.e.send_tx(currency, quantity, address, memo)
		except:
			time.sleep(self.time_out)
			return self.e.send_tx(currency, quantity, address, memo)

	def get_balance(self, currency):
		try:
			return float(self.e.get_balance(currency))
		except:
			time.sleep(self.time_out)
			return float(self.e.get_balance(currency))

	def order_complete(self, orderId, market):
		try:
			return bool(self.e.order_complete(orderId, market))
		except:
			time.sleep(self.time_out)
			return bool(self.e.order_complete(orderId, market))

	def get_open_orders(self, market):
		try:
			return self.e.get_open_orders(market)
		except:
			time.sleep(self.time_out)
			return self.e.get_open_orders(market)

	def cancel(self, market, orderId):
		try:
			return self.e.cancel(market, orderId)
		except:
			time.sleep(self.time_out)
			return self.e.cancel(market, orderId)

	def stop_buy(self, market, amount, price, stop_limit):
		try:
			return self.e.stop_buy(market, amount, price, stop_limit)
		except:
			time.sleep(self.time_out)
			return self.e.stop_buy(market, amount, price, stop_limit)

	def stop_sell(self, market, amount, price, stop_limit):
		try:
			return self.e.stop_sell(market, amount, price, stop_limit)
		except:
			time.sleep(self.time_out)
			return self.e.stop_sell(market, amount, price, stop_limit)