import hashlib
import hmac
import requests
import json
import time
import base64
from exchanges import cbauth
# import cbauth
import os

class CB:
	def __init__(self, secret, key, passphrase):
		self.secret=secret
		self.key=key
		self.base="https://api.pro.coinbase.com"
		self.base_sandbox="https://api-public.sandbox.pro.coinbase.com"
		self.passphrase=passphrase
		self.fees=.005
		# self.auth=cbauth.CBProAuth(key, secret, passphrase)

	def sign(self, method, url, body, ts):
		if body:
			b = json.dumps(body)
		else:
			b = ''
		u = url.replace(self.base,'')
		message = "{0}{1}{2}{3}".format(ts, method, u, b)
		return cbauth.get_auth_headers(ts, message, self.key, self.secret, self.passphrase)

	def get_timestamp(self):
		url = self.base + "/time"
		r = requests.get(url)
		return r.json()

	def get_epoch_timestamp(self):
		return str(self.get_timestamp()["epoch"])

	def get_iso_timestamp(self):
		return str(self.get_timestamp()["iso"])

	def get_headers(self, method, url, body=None):
		ts = self.get_epoch_timestamp()
		sign = self.sign(method, url, body, ts)
		return sign

	def pathstring(self, params):
		ps = ""
		for i in range(len(list(params.keys()))):
			key = list(params.keys())[i]
			if i > 0 and params[key] is not None:
				symbol = "&"
			elif params[key] is not None:
				symbol = "?"
			else:
				continue
			ps="{0}{1}{2}={3}".format(ps,symbol, key,params[str(key)])
		return ps

	def get_products(self):
		url = self.base + "/products"
		r = requests.get(url)
		return r.json()

	def get_order_book(self, market):
		url = self.base + "/products/{0}/book".format(market)
		params = {"level":1}
		r = requests.get(url, params=params)
		return r.json()

	def get_buy_price(self, market):
		return self.get_order_book(market)['bids'][0][0]

	def get_sell_price(self, market):
		return self.get_order_book(market)['asks'][0][0]

	def place_order(self, otype, side, market, stp=None, stop=None, stop_price=None, cid=None, price=None, time_in_force=None, size=None, cancel_after=None, post_only=None, funds=None):
		body = {
			"type":otype,
			"side":side,
			"product_id":market,
			"stp":stp,
			"stop":stop,
			"stop_price":stop_price,
			"client_oid":cid,
			"price":price,
			"time_in_force":time_in_force,
			"size":size,
			"cancel_after":cancel_after,
			"post_only":post_only,
			"funds":funds,
		}
		url = self.base + "/orders"
		headers = self.get_headers("POST", url, body)
		r = requests.post(url=url, headers=headers, json=body)
		# print(r.status_code)
		return r.json()

	def place_order(self, otype, side, market, stp=None, stop=None, stop_price=None, cid=None, price=None, time_in_force=None, size=None, cancel_after=None, post_only=None, funds=None):
		body = {
			"type":otype,
			"side":side,
			"product_id":market,
			"stp":stp,
			"stop":stop,
			"stop_price":stop_price,
			"client_oid":cid,
			"price":price,
			"time_in_force":time_in_force,
			"size":size,
			"cancel_after":cancel_after,
			"post_only":post_only,
			"funds":funds,
		}
		url = self.base + "/orders"
		headers = self.get_headers("POST", url, body)
		r = requests.post(url=url, headers=headers, json=body)
		# print(r.status_code)
		return r.json()

	def buy(self, market, amount, price, order_type=None, addtl_params={}):
		if order_type==None:
			return place_order('limit', "buy", market, price=price)
		elif order_type=="market":
			return place_order(order_type, "buy", market)
		elif order_type=="stop":
			return place_order("limit", "buy", market, price=price, stop="entry", stop_price=addtl_params.get("stop_price"))
		elif order_type == "stopmarket":
			return place_order("market", "buy", market, price=price, stop="entry", stop_price=addtl_params.get("stop_price"))
		else:
			return None

	def sell(self, market, amount, price, order_type=None, addtl_params={}):
		if order_type==None:
			return place_order('limit', "sell", market, price=price)
		elif order_type=="market":
			return place_order(order_type, "sell", market)
		elif order_type=="stop":
			return place_order("limit", "sell", market, price=price, stop="loss", stop_price=addtl_params.get("stop_price"))
		elif order_type == "stopmarket":
			return place_order("market", "sell", market, price=price, stop="loss", stop_price=addtl_params.get("stop_price"))
		else:
			return None

	def cancel_order(self, order_id, product_id=None):
		params = {"product_id":product_id}
		url = self.base + "/orders{0}{1}".format(order_id, self.pathstring(params))
		headers = self.get_headers("DELETE", url)
		r = requests.delete(url=url, headers=headers, params=params)
		# print(r.status_code)
		return r.json()

	def list_orders(self, status=None, product_id=None):
		params={
			"status":status,
			"product_id":product_id
		}
		url = self.base + "/orders{0}".format(self.pathstring(params))
		headers = self.get_headers("GET", url)
		r = requests.get(url=url, headers=headers)
		# print(r.status_code)
		return r.json()

	def get_order(self, order_id):
		url = self.base + "/orders/{0}".format(order_id)
		headers = self.get_headers("GET", url)
		r = requests.get(url=url, headers=headers)
		# print(r.status_code)
		return r.json()

	def list_accounts(self):
		url = self.base + "/accounts"
		headers = self.get_headers("GET", url)
		r = requests.get(url=url, headers=headers)
		# print(r.status_code)
		return r.json()

	def get_balance(self, currency):
		return [x["balance"] for x in self.list_accounts() if x["currency"] == currency][0]

	def list_payment_methods(self):
		url = self.base + "/payment-methods"
		headers = self.get_headers("GET", url)
		r = requests.get(url=url, headers=headers)
		# print(r.status_code)
		return r.json()

	def deposit(self, amount, currency, payment_method_id):
		body = {
			"amount":amount,
			"currency":currency,
			"payment_method_id":payment_method_id
		}
		url = self.base + "/deposits/payment-method"
		headers = self.get_headers("POST", url, body)
		r = requests.post(url=url, headers=headers, json=body)
		# print(r.status_code)
		return r.json()

	def withdraw(self, amount, currency, payment_method_id):
		body = {
			"amount":amount,
			"currency":currency,
			"payment_method_id":payment_method_id
		}
		url = self.base + "/withdrawals/payment-method"
		headers = self.get_headers("POST", url, body)
		r = requests.post(url=url, headers=headers, json=body)
		# print(r.status_code)
		return r.json()

	def send_tx(self, currency, amount, crypto_address, destination_tag=None):
		if destination_tag is not None:
			no_destination_tag = False
		else:
			no_destination_tag = True
		body = {
			"amount":amount,
			"currency":currency,
			"crypto_address":crypto_address,
			"destination_tag":destination_tag,
			"no_destination_tag":no_destination_tag,
		}
		url = self.base + "/withdrawals/crypto"
		headers = self.get_headers("POST", url, body)
		r = requests.post(url=url, headers=headers, json=body)
		# print(r.status_code)
		return r.json()

# secret, key, passphrase = os.environ["CB_SECRET"], os.environ["CB_KEY"], os.environ["CB_PASSPHRASE"]
# c = CB(secret, key, passphrase)
# print(json.dumps(c.get_balance("XRP")))


