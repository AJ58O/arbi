import os
import requests
import hmac
import hashlib
import base64
import time

######API CALLS

class binance_api:
	def __init__(self, key, secret):
		self.key = key
		self.secret = secret.encode("utf-8")
		self.baseURL = "https://api.binance.com"
		self.pingURL = "/api/v1/ping"
		self.timeURL = "/api/v1/time"
		self.bookURL = "/api/v1/depth"
		self.recentTradeURL = "/api/v1/trades"
		self.historicalTradeURL = "/api/v1/historicalTrades"
		self.rangeTradeURL = "/api/v1/aggTrades"
		self.candlestickURL = "/api/v1/klines"
		self.dayURL="/api/v1/ticker/24hr"
		self.priceURL = "/api/v3/ticker/price"
		self.bookTickerURL="/api/v3/ticker/bookTicker"
		self.testNewOrderURL = "/api/v3/order/test"
		self.orderURL="/api/v3/order"
		self.openOrdersURL="/api/v3/openOrders"
		self.allOrdersURL="/api/v3/allOrders"
		self.accountInfoURL="/api/v3/account"
		self.accountTradesURL="/api/v3/myTrades"
		self.withdrawURL="/wapi/v3/withdraw.html"

	def getSignature(self, message):
		#returns a signature
		dig = hmac.new(self.secret, msg=message, digestmod=hashlib.sha256).hexdigest()
		return dig

	def is_connected(self):
		#returns true if status=200, otherwise false
		url = f"{self.baseURL}{self.pingURL}"
		if requests.get(url).status_code==200:
			return True 
		else:
			return False 

	def getTimestamp(self):
		#returns timestamp of binance servers
		r = requests.get(f"{self.baseURL}{self.timeURL}").json()
		return r.get('serverTime')

	def getOrderBook(self, symbol, limit=None):
		#returns current order book
		return requests.get(f"{self.baseURL}{self.bookURL}", params={"symbol":symbol,"limit":limit}).json()

	def getRecentTrades(self, symbol, limit=None):
		#returns recent trades
		return requests.get(f"{self.baseURL}{self.recentTradeURL}", params={"symbol":symbol, "limit":limit}).json()

	def getHistoricalTrade(self, symbol, limit=None, fromId=None):
		#returns historical trade
		return requests.get(f"{self.baseURL}{self.historicalTradeURL}", headers={"X-MBX-APIKEY":self.key},params={"symbol":symbol, "limit":limit, "fromId":fromId}).json()

	def getTradesByTimeRange(self, symbol, startTime=None, endTime=None, limit=None, fromId=None):
		#returns trades in a timeframe
		return requests.get(f"{self.baseURL}{self.rangeTradeURL}",headers={"X-MBX-APIKEY":self.key}, params={"symbol":symbol, "limit":limit, "fromId":fromId, "startTime":startTime, "endTime":endTime}).json()

	def getCandleStick(self, symbol, interval, limit=None, startTime=None, endTime=None):
		#returns candlestick data
		#interval values can be:
		# "1m","3m","5m","15m","30m","1h","2h","4h","6h","8h","12h","1d","3d","1w", "1M"
		return requests.get(f"{self.baseURL}{self.candlestickURL}", headers={"X-MBX-APIKEY":self.key},params={"symbol":symbol, "limit":limit, "interval":interval, "startTime":startTime, "endTime":endTime}).json()

	def get24HrSwing(self, symbol=None):
		#returns 24hr data
		return requests.get(f"{self.baseURL}{self.dayURL}", headers={"X-MBX-APIKEY":self.key},params={"symbol":symbol}).json()

	def getPrice(self, symbol=None):
		#returns price data
		return requests.get(f"{self.baseURL}{self.priceURL}", headers={"X-MBX-APIKEY":self.key},params={"symbol":symbol}).json()

	def getBookTicker(self, symbol=None):
		#returns price/qty data
		return requests.get(f"{self.baseURL}{self.bookTickerURL}", headers={"X-MBX-APIKEY":self.key},params={"symbol":symbol}).json()

	def newOrder(self, symbol, side, orderType, quantity, timeInForce=None, price=None, newClientOrderId=None, stopPrice=None, newOrderRespType=None, recvWindow=None, live=False):
		timestamp=self.getTimestamp()
		#submits a new order
		if live != True:
			orderURL = testNewOrderURL
		data = {
				"symbol":symbol, 
				"side":side, 
				"type":orderType, 
				"quantity":quantity, 
				"timestamp":timestamp, 
				}
		message = "symbol={0}&side={1}&type={2}&quantity={3}&timestamp={4}".format(symbol, side, orderType, quantity, timestamp)
		if timeInForce != None:
			message+="&timeInForce={}".format(timeInForce)
			data['timeInForce']=timeInForce
		if price != None:
			message+="&price={}".format(price)
			data['price']=price
		if newClientOrderId != None:
			message+="&newClientOrderId={}".format(newClientOrderId)
			data['newClientOrderId']=newClientOrderId
		if stopPrice != None:
			message+="&stopPrice={}".format(stopPrice)
			data['stopPrice']=stopPrice
		if newOrderRespType!=None:
			message+="&newOrderRespType={}".format(newOrderRespType)
			data['newOrderRespType']=newOrderRespType
		if recvWindow!=None:
			message+="&recvWindow={}".format(recvWindow)
			data['recvWindow']=recvWindow
		signature = self.getSignature(message.encode('utf-8'))
		data['signature']=signature
		
		return requests.post(f"{self.baseURL}{self.orderURL}", headers={"X-MBX-APIKEY":self.key}, data=data).json()
		

	def getOrderStatus(self, symbol, orderId=None, origClientId=None, recvWindow=None):
		timestamp=self.getTimestamp()
		#returns an order status
		message="symbol={0}&timestamp={1}".format(symbol, timestamp)
		params={
			"symbol":symbol,
			"timestamp":timestamp,
		}
		if orderId:
			params['orderId']=orderId
			message+="&orderId={}".format(orderId)
		if origClientId:
			params['origClientId']=origClientId
			message+="&origClientId={}".format(origClientId)
		if recvWindow:
			params['recvWindow']=recvWindow
			message+="&recvWindow={}".format(recvWindow)
		signature = self.getSignature(message.encode('utf-8'))
		params['signature']=signature
		return requests.get(f"{self.baseURL}{self.orderURL}", headers={"X-MBX-APIKEY":self.key}, params=params).json()

	def cancelOrder(self, symbol, orderId=None, origClientId=None, newClientOrderId=None, recvWindow=None):
		timestamp=self.getTimestamp()
		#cancels an order
		message="symbol={0}&timestamp={1}".format(symbol, timestamp)
		params={
			"symbol":symbol,
			"timestamp":timestamp,
		}
		if orderId:
			params['orderId']=orderId
			message+="&orderId={}".format(orderId)
		if origClientId:
			params['origClientId']=origClientId
			message+="&origClientId={}".format(origClientId)
		if recvWindow:
			params['recvWindow']=recvWindow
			message+="&recvWindow={}".format(recvWindow)
		if newClientOrderId:
			params['newClientOrderId']=newClientOrderId
			message+="&newClientOrderId={}".format(newClientOrderId)
		signature = self.getSignature(message.encode('utf-8'))
		params['signature']=signature

		keepPollingOrder = True
		return requests.delete(f"{self.baseURL}{self.orderURL}",headers={"X-MBX-APIKEY":self.key}, params=params).json()

	def getOpenOrders(self, symbol=None, recvWindow=None):
		#gets open orders
		timestamp=self.getTimestamp()
		print(timestamp)
		message = "timestamp={}".format(timestamp)
		params={
			"timestamp":timestamp
		}
		if symbol:
			params['symbol']=symbol
			message+="&symbol={}".format(symbol)
		if recvWindow:
			params['recvWindow']=recvWindow
			message+="&recvWindow=&{}".format(recvWindow)
		signature = self.getSignature(message.encode('utf-8'))
		params['signature']=signature

		keepPollingOpenOrders = True
		return requests.get(f"{self.baseURL}{self.openOrdersURL}", headers={"X-MBX-APIKEY":self.key}, params=params).json()

	def getAllOrders(self, symbol, recvWindow=None, limit=None, orderId=None):
		timestamp=self.getTimestamp()
		#returns all orders
		message="symbol={0}&timestamp={1}".format(symbol, timestamp)
		params={
			"symbol":symbol,
			"timestamp":timestamp,
		}
		if orderId:
			params['orderId']=orderId
			message+="&orderId={}".format(orderId)
		if limit:
			params['limit']=limit
			message+="&limit={}".format(limit)
		if recvWindow:
			params['recvWindow']=recvWindow
			message+="&recvWindow={}".format(recvWindow)
		signature = self.getSignature(message.encode('utf-8'))
		params['signature']=signature
		return requests.get(f"{self.baseURL}{self.allOrdersURL}", headers={"X-MBX-APIKEY":self.key}, params=params).json()

	def getAccountInfo(self, recvWindow=None):
		timestamp=self.getTimestamp()
		#gets account info
		message="timestamp={}".format(timestamp)
		params={
			"timestamp":timestamp
		}
		if recvWindow:
			params['recvWindow']=recvWindow
			message+="&recvWindow={}".format(recvWindow)
		signature = self.getSignature(message.encode('utf-8'))
		params['signature']=signature
		return requests.get(f"{self.baseURL}{self.accountInfoURL}", headers={"X-MBX-APIKEY":self.key}, params=params).json()
		

	def getTrades(self, symbol, limit=None, fromId=None, recvWindow=None):
		timestamp=self.getTimestamp()
		#gets account trades
		message="symbol={0}&timestamp={1}".format(symbol, timestamp)
		params={
			"symbol":symbol,
			"timestamp":timestamp,
		}
		if recvWindow:
			params['recvWindow']=recvWindow
			message+="&recvWindow={}".format(recvWindow)
		if limit:
			params['limit']=limit
			message+="&limit={}".format(limit)
		if fromId:
			params['fromId']=fromId
			message+="&fromId={}".format(fromId)
		signature = self.getSignature(message.encode('utf-8'))
		params['signature']=signature
		return requests.get(f"{self.baseURL}{self.accountTradesURL}", headers={"X-MBX-APIKEY":self.key}, params=params).json()

	def withdraw(self, asset, address, amount, network=None, memo=None, name=None, recvWindow=None):
		timestamp=self.getTimestamp()
		#gets account trades
		message="asset={0}&address={1}&amount={2}&timestamp={3}".format(asset, address, amount, timestamp)
		params={
			"asset":asset,
			"address":address,
			"amount":amount,
			"timestamp":timestamp
		}
		if recvWindow:
			params['recvWindow']=recvWindow
			message+="&recvWindow={}".format(recvWindow)
		if name:
			params['name']=name
			message+="&name={}".format(name)
		if memo:
			params['memo']=memo
			message+="&memo={}".format(memo)
		if network:
			params['network']=network
			message+="&network={}".format(network)			
		signature = self.getSignature(message.encode('utf-8'))
		params['signature']=signature
		return requests.post(f"{self.baseURL}{self.withdrawURL}", headers={"X-MBX-APIKEY":self.key}, params=params).json()

	##Exchange class functions

	def get_buy_price(self, market):
		return self.getBookTicker(market)["bidPrice"]

	def get_sell_price(self, market):
		return self.getBookTicker(market)["askPrice"]

	def buy(self, market, amount, price, order_type=None, addtl_params=None):
		return self.newOrder(market, "BUY", "LIMIT", amount, live=True, price=price)

	def sell(self, market, amount, price, order_type=None, addtl_params=None):
		return self.newOrder(market, "SELL", "LIMIT", amount, price=price)

	def get_balance(self, currency):
		return [x["free"] for x in self.getAccountInfo()['balances'] if x["asset"] == currency][0]

	def send_tx(self, currency, quantity, address, memo):
		return self.withdraw(currency, address, quantity, memo=memo)

b = binance_api(os.environ["BINANCE_KEY"], os.environ["BINANCE_SECRET"])
print(b.get_balance("XRP"))