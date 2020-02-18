import requests
import json
import time

class bitrue:
	def __init__(self, secret, key):
		self.secret = secret
		self.key = key
		self.base = "https://www.bitrue.com"

	def sign(self, message, secret_key):
		return = hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()

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

	def get_headers(self):
		return {
			"X-MBX-APIKEY":self.key
		}

	def add_signature(self, body, params):
		pathstring = self.pathstring(params)
		total_params = "{0}{1}".format(pathstring, json.dumps(body))
		signature = self.sign(total_params, self.secret)
		body["signature"] = signature
		return body

