from exchanges import bittrex_api
from exchanges import coinbase_api
from exchanges.exchange_class import Exchange
import datetime
import time
import json
import os
import random

class arbitrage:
	def __init__(self, exchange1, exchange2, pair1, pair2, amount1, amount2, price1=None, price2=None, run_op=False, threshhold=None):
		self.exchange1=exchange1
		self.exchange2=exchange2
		self.pair1=pair1
		self.pair2=pair2
		self.amount1=amount1
		self.amount2=amount2
		self.price1=price1
		self.price2=price2
		if threshhold==None:
			self.threshhold=.01
		else:
			self.threshhold = threshhold
		if run_op == True:
			self.get_opportunity()

	def get_opportunity(self, r=None):
		if self.price1 == None:
			self.price1 = float(self.exchange1.get_buy_price(self.pair1))
		if self.price2 == None:
			self.price2 = float(self.exchange2.get_sell_price(self.pair2))
		if self.price1==self.price2:
			return False
		self.priceDiff = abs(float(self.price1)-float(self.price2)) 
		self.lowestPrice = min(float(self.price1), float(self.price2)) 
		self.margin = self.priceDiff/self.lowestPrice #return margin as a percent of the smaller price (% increase)

		if self.lowestPrice == self.price1:
			self.sell_exchange = self.exchange2
			self.buy_exchange = self.exchange1
			self.sell_pair = self.pair2
			self.buy_pair = self.pair1
			self.sell_price = self.price2
			self.buy_price = self.price1
			self.sell_amount = self.amount2
			self.buy_amount = self.amount1
		else:
			self.sell_exchange = self.exchange1
			self.buy_exchange = self.exchange2
			self.sell_pair = self.pair1
			self.buy_pair = self.pair2
			self.sell_price = self.price1
			self.buy_price = self.price2
			self.sell_amount = self.amount1
			self.buy_amount = self.amount2

		self.get_suggested_amounts()

		self.sell_margin = (float(self.sell_amount)*float(self.sell_price)) - float(self.buy_amount) #how much more of the asset I used to buy did I end up with?
		self.buy_margin = float(self.sell_amount)-(float(self.buy_amount/float(self.buy_price))) #how much more of the assed I sold did I end up with?

		self.make_trade_decision(self.threshhold)
		self.log_everything()

		printString = '''\
		---------------
		PriceDiff: {priceDiff}
		Margin: {margin}
		SellExchange: {sell_exchange_name}
		BuyExchange: {buy_exchange_name}
		SellPair: {sell_pair}
		BuyPair: {buy_pair}
		SellPrice: {sell_price}
		BuyPrice: {buy_price}
		SellAmount: {sell_amount}
		BuyAmount: {buy_amount}
		SellMargin: {sell_margin}
		BuyMargin: {buy_margin}
		SuggestedBuyAmount: {suggested_buy_amount}
		SuggestedSellAmount: {suggested_sell_amount}
		GrossMargin: {gross_margin}
		DoTrade?: {trade_decision}
		---------------
		'''.format(
				priceDiff = self.priceDiff,
				margin = self.margin,
				sell_exchange_name = self.sell_exchange.name,
				buy_exchange_name = self.buy_exchange.name,
				sell_pair = self.sell_pair,
				buy_pair = self.buy_pair,
				sell_price = self.sell_price,
				buy_price = self.buy_price,
				sell_amount = self.sell_amount,
				buy_amount = self.buy_amount,
				sell_margin = self.sell_margin,
				buy_margin = self.buy_margin,
				suggested_buy_amount = self.suggested_buy_amount,
				suggested_sell_amount = self.suggested_sell_amount,
				gross_margin = self.gross_margin,
				trade_decision = self.do_trade
			)
		print(printString)
		if r is not None:
			return self.sell_exchange.name, self.priceDiff, self.margin

	def get_suggested_amounts(self):
		self.suggested_buy_amount = min(float(self.buy_amount), float(self.sell_amount) * float(self.sell_price))
		self.suggested_sell_amount = min(float(self.sell_amount), float(self.buy_amount) / float(self.buy_price))
		
		self.gross_margin = (float(self.suggested_buy_amount) / float(self.buy_price) * float(self.sell_price)) - float(self.suggested_buy_amount)

	def make_trade_decision(self, threshhold):
		if float(self.margin) > threshhold:
			self.do_trade = True
		else:
			self.do_trade = False

	def log_everything(self):
		with open("log.txt", "a") as text_file:
			text_file.write(
					'{ts},{priceDiff},{margin},{sell_exchange_name},{buy_exchange_name},{sell_pair},{buy_pair},{sell_price},{buy_price},{sell_amount},{buy_amount},{sell_margin},{buy_margin},{suggested_buy_amount},{suggested_sell_amount},{gross_margin},{trade_decision}\n'.format(
						ts = datetime.datetime.now(),
						priceDiff = self.priceDiff,
						margin = self.margin,
						sell_exchange_name = self.sell_exchange.name,
						buy_exchange_name = self.buy_exchange.name,
						sell_pair = self.sell_pair,
						buy_pair = self.buy_pair,
						sell_price = self.sell_price,
						buy_price = self.buy_price,
						sell_amount = self.sell_amount,
						buy_amount = self.buy_amount,
						sell_margin = self.sell_margin,
						buy_margin = self.buy_margin,
						suggested_buy_amount = self.suggested_buy_amount,
						suggested_sell_amount = self.suggested_sell_amount,
						gross_margin = self.gross_margin,
						trade_decision = self.do_trade
					)
				)

		
	def execute(self):
		sell = self.sell_exchange.sell(self.sell_pair, self.suggested_sell_amount, self.sell_price)
		buy = self.buy_exchange.buy(self.buy_pair, self.suggested_buy_amount, self.buy_price)

	def rebalance(self):
		curs = self.pair1.split("-")
		self.cur1 = curs[0]
		self.cur2 = curs[1]
		self.sellbal1 = sell_exchange.get_balance(self.cur1)
		self.buybal1 = buy_exchange.get_balance(self.cur1)
		self.sellbal2 = sell_exchange.get_balance(self.cur2)
		self.buybal2 = buy_exchange.get_balance(self.cur2)

		self.cur1balamount = (float(self.sellbal1) + float(self.buybal1)) / 2
		self.cur2balamount = (float(self.sellbal2) + float(self.buybal2)) / 2

		if self.cur1balamount > self.sellbal1:
			amount = self.cur1balamount - self.sellbal1
			buy_exchange.send_tx(self.cur1, amount, sell_exchange.wallet[self.cur1]["address"], sell_exchange.wallet[self.cur1]["memo"])
		elif self.cur1balamount > self.buybal1:
			amount = self.cur1balamount - self.buybal1
			sell_exchange.send_tx(self.cur1, amount, buy_exchange.wallet[self.cur1]["address"], buy_exchange.wallet[self.cur1]["memo"])

		if self.cur2balamount > self.sellbal2:
			amount = self.cur2balamount - self.sellbal2
			buy_exchange.send_tx(self.cur2, amount, sell_exchange.wallet[self.cur2]["address"], sell_exchange.wallet[self.cur2]["memo"])
		elif self.cur2balamount > self.buybal2:
			amount = self.cur2balamount - self.buybal2
			sell_exchange.send_tx(self.cur2, amount, buy_exchange.wallet[self.cur2]["address"], buy_exchange.wallet[self.cur2]["memo"])

	def rebalance_complete(self):
		sellbal1 = sell_exchange.get_balance(self.cur1)
		buybal1 = buy_exchange.get_balance(self.cur1)
		sellbal2 = sell_exchange.get_balance(self.cur2)
		buybal2 = buy_exchange.get_balance(self.cur2)

		if max(sellbal1, buybal1) < max(self.sellbal1, self.buybal1) and max(sellbal2, buybal2) < max(self.sellbal2, self.buybal2):
			return True
		return False