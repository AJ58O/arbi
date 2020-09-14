import hashlib
import hmac
import requests
import json
import time
import os

class bittrex_api:
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

	def normalize_pair(self, pair):
		curs = pair.split("-")
		return f"{curs[1]}-{curs[0]}"


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
			return self.get_order_book(self.normalize_pair(market), "buy")["result"][0]["Rate"]
		except:
			return self.get_order_book(self.normalize_pair(market), "buy")

	def get_sell_price(self, market):
		try:
			return self.get_order_book(self.normalize_pair(market), "sell")["result"][0]["Rate"]
		except:
			return self.get_order_book(self.normalize_pair(market), "sell")

	def send_tx(self, currency, quantity, address, memo=None):
		params = {
			"currency":currency,
			"quantity":quantity,
			"address":address,			
			"nonce":str(time.time()).split(".")[0],
			"apikey":self.key
		}
		if memo != None:
			params["paymentid"] = memo
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
		market = self.normalize_pair(market)
		print(market)
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
		if r.json()["result"]["Balance"] == None:
			return "0"
		return r.json()["result"]["Balance"]

	def cancel(self, symbol, uuid):
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
			"market":self.normalize_pair(market),
			"quantity":quantity,
			"rate":rate,
			"timeInForce":"GTC",
			"nonce":str(time.time()).split(".")[0],
			"apikey":self.key
		}
		url = self.base + "/market/selllimit"+self.pathstring(params)
		headers = {
			"apisign":self.sign(url),
			"Content-Type":"application/json"
		}
		r = requests.get(url, headers=headers).json()
		try:
			return r["result"]["uuid"]
		except:
			print("except")
			print(r)
			return r

	def buy(self, market, quantity, rate, order_type=None, addtl_params={}):
		params = {
			"market":self.normalize_pair(market),
			"quantity":quantity,
			"rate":rate,
			"timeInForce":"GTC",
			"nonce":str(time.time()).split(".")[0],
			"apikey":self.key
		}
		url = self.base + "/market/buylimit"+self.pathstring(params)
		headers = {
			"apisign":self.sign(url),
			"Content-Type":"application/json"
		}
		r = requests.get(url, headers=headers)
		resp = r.json()
		try:
			return resp["result"]["uuid"]
		except:
			print("except")
			print(resp)
			return resp

	def order_complete(self, orderId, market):
		print(orderId)
		print(self.get_order(orderId))
		return not bool(self.get_order(orderId)["result"]["IsOpen"])

		
# b = bittrex_api(os.environ["BITTREX_SECRET"], os.environ["BITTREX_KEY"])
# print(b.order_complete("XRP-USDT", "bae21960-8bf2-4f20-a443-02e7028bf053"))