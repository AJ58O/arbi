import hashlib
import hmac
import requests
import json
import time
import os

class Bittrex:
	def __init__(self, secret, key):
		self.secret=secret.encode()
		self.key=key
		self.base="https://api.bittrex.com/api/v1.1"
		self.fees=.0025
	
	def sign(self, url):
		return hmac.new(self.secret, url.encode("utf-8"), hashlib.sha512).hexdigest()

	def pathstring(self, params):
		ps = ""
		for i in range(len(list(params.keys()))):
			key = list(params.keys())[i]
			if i > 0:
				symbol = "&"
			else:
				symbol = "?"
			ps="{0}{1}{2}={3}".format(ps,symbol, key,params[str(key)])
			# print(ps)
		return ps


	def get_order_book(self, market, order_type):
		params = {
			"market":market,
			"type":order_type,
			"nonce":str(time.time()).split(".")[0],
			"apikey":self.key
		}
		url = self.base + "/public/getorderbook"+self.pathstring(params)
		# print(url)
		headers = {
			"apisign":self.sign(url),
			"Content-Type":"application/json"
		}
		r = requests.get(url, headers=headers)
		# print(r.json())
		return r.json()

	def get_buy_price(self, market):
		# print(market)
		try:
			return self.get_order_book(market, "buy")["result"][0]["Rate"]
		except:
			return self.get_order_book(market, "buy")

	def get_sell_price(self, market):
		try:
			return self.get_order_book(market, "sell")["result"][0]["Rate"]
		except:
			return self.get_order_book(market, "sell")

	def send_tx(self, currency, quantity, address, paymentid=None):
		params = {
			"currency":currency,
			"quantity":quantity,
			"address":address,
			"paymentid":paymentid,
			"nonce":str(time.time()).split(".")[0],
			"apikey":self.key
		}
		url = self.base + "/account/withdraw"+self.pathstring(params)
		headers = {
			"apisign":self.sign(url),
			"Content-Type":"application/json"
		}
		r = requests.get(url, headers=headers)
		return r.json()
		
	def get_order(self, uuid):
		params = {
			"uuid":uuid,
			"nonce":str(time.time()).split(".")[0],
			"apikey":self.key
		}
		url = self.base + "/account/getorder"+self.pathstring(params)
		headers = {
			"apisign":self.sign(url),
			"Content-Type":"application/json"
		}
		r = requests.get(url, headers=headers)
		return r.json()

	def get_open_orders(self, market):
		params = {
			"market":market,
			"nonce":str(time.time()).split(".")[0],
			"apikey":self.key
		}
		url = self.base + "/market/getopenorders"+self.pathstring(params)
		headers = {
			"apisign":self.sign(url),
			"Content-Type":"application/json"
		}
		r = requests.get(url, headers=headers)
		return r.json()

	def get_balances(self):
		params = {
			"nonce":str(time.time()).split(".")[0],
			"apikey":self.key
		}
		url = self.base + "/account/getbalances"+self.pathstring(params)
		headers = {
			"apisign":self.sign(url),
			"Content-Type":"application/json"
		}
		r = requests.get(url, headers=headers)
		return r.json()

	def get_balance(self, currency):
		params = {
			"currency":currency,
			"nonce":str(time.time()).split(".")[0],
			"apikey":self.key
		}
		url = self.base + "/account/getbalance"+self.pathstring(params)
		headers = {
			"apisign":self.sign(url),
			"Content-Type":"application/json"
		}
		r = requests.get(url, headers=headers)
		return r.json()["result"]["Balance"]

	def cancel(self, uuid):
		params = {
			"uuid":uuid,
			"nonce":str(time.time()).split(".")[0],
			"apikey":self.key
		}
		url = self.base + "/market/cancel"+self.pathstring(params)
		headers = {
			"apisign":self.sign(url),
			"Content-Type":"application/json"
		}
		r = requests.get(url, headers=headers)
		return r.json()
		
	def sell(self, market, quantity, rate, order_type=None, addtl_params={}):
		params = {
			"quantity":quantity,
			"rate":rate,
			"timeInForce":timeInForce,
			"nonce":str(time.time()).split(".")[0],
			"apikey":self.key
		}
		url = self.base + "/market/selllimit"+self.pathstring(params)
		headers = {
			"apisign":self.sign(url),
			"Content-Type":"application/json"
		}
		r = requests.get(url, headers=headers)
		return r.json()

	def buy(self, market, quantity, rate, order_type=None, addtl_params={}):
		params = {
			"quantity":quantity,
			"rate":rate,
			"timeInForce":timeInForce,
			"nonce":str(time.time()).split(".")[0],
			"apikey":self.key
		}
		url = self.base + "/market/buylimit"+self.pathstring(params)
		headers = {
			"apisign":self.sign(url),
			"Content-Type":"application/json"
		}
		r = requests.get(url, headers=headers)
		return r.json()

	def order_complete(self, market, orderId):
		return self.get_order(orderId)
		
# b = Bittrex(os.environ["BITTREX_SECRET"], os.environ["BITTREX_KEY"])
# print(json.dumps(b.get_balance("XRP")))