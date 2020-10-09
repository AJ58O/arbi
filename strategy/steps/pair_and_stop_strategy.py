from exchanges.apis import binance_api
from exchanges.exchange_class import Exchange
from os import environ
from os import path
from time import sleep
from strategy.clients.paired_trade_client import paired_trade_client
from strategy.clients.stop_client import StopClient
import datetime
import traceback
import sys


class PairAndStopStrategy:
	def __init__(self, config):
		self.config = config
		self.stratList = config["stratList"]
		self.active_trade_obj = {}
		self.hours_until_expiration = hours_until_expiration
		self.logfile = "trade_log.txt"
		self.paired_trade_list = []
		self.stop_trade_list = []

		if not path.exists(self.logfile):
			with open(self.logfile, "a") as text_file:
				text_file.write(f"ts,exchange,pair,buy amount,buy price,sell amount,sell price,buy,sell,init_buy_bal,init_sell_bal,final_sell_bal,final_buy_bal\n")
		
	def initialize():
		for strat in self.stratList:
			name = strat.get("name")
			threshhold = strat.get("threshhold")
			alloc_of_total_balance = strat.get("alloc_of_total_balance")
			pair = strat.get("pair")
			exchanges = strat.get("exchanges")
			trade_amount = strat.get("alloc_of_total_balance")
			strat_id = strat.get("id")

			for exchange in exchanges:
				if name == "simple_pair_trading":
					try:
						trade = paired_trade_client(exchange, pair, threshhold, trade_amount, run_trade=True)
						self.paired_trade_list.append({"strat":strat,"trade":trade})
						self.active_trade_obj[f"{exchange.name}_{strat_id}"] = {}
						self.active_trade_obj[f"{exchange.name}_{strat_id}"]["TradeActive"] = True
						self.active_trade_obj[f"{exchange.name}_{strat_id}"]["buy"] = trade.buy
						self.active_trade_obj[f"{exchange.name}_{strat_id}"]["sell"] = trade.sell
						self.active_trade_obj[f"{exchange.name}_{strat_id}"]["expiration"] = None #set this only when we can determine a single trade has closed
					except:
						traceback.print_exc()
				elif name == "stop_trading":
					try:
						stop_trade = StopClient(exchange, pair, threshhold, trade_amount)
						self.stop_trade_list.append({"strat":strat, "trade":stop_trade})
						stop_trade.do_trade()
					except:
						traceback.print_exc()

		sleep(5)
	
	def run_interval(self):
		for t in self.paired_trade_list:
			try:
				if t["trade"].trade_complete():
					self.active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["TradeActive"] = False
					self.active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["buy"] = None
					self.active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["sell"] = None
					self.active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["expiration"] = None
					t["trade"] = None
				elif t["trade"].only_one_trade_complete():
					if self.active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["expiration"] == None:
						self.active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["expiration"] = datetime.datetime.now() + datetime.timedelta(hours=self.hours_until_expiration)
					elif self.active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["expiration"] < datetime.datetime.now():
						t["trade"].cancel_open_trade()
						self.active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["TradeActive"] = False
						self.active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["buy"] = None
						self.active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["sell"] = None
						self.active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["expiration"] = None
						t["trade"] = None
			except:
					traceback.print_exc()
		for key in self.active_trade_obj.keys():
			if self.active_trade_obj[key]["TradeActive"] == False:
				echanges = [ s["exchanges"] for s in self.stratList if s["id"] == key.split("_")[1] ][0]
				exchange = [e for e in exchanges if e.name in key][0]
				strat = [s for s in self.paired_trade_list if s["trade"] == None][0]
				strat_id = strat.get("id")
				threshhold = strat.get("threshhold")
				pair = strat.get("pair")
				trade_amount = strat.get("alloc_of_total_balance")
				try:
					trade = paired_trade_client(exchange, pair, threshhold, trade_amount, run_trade=True)
					self.paired_trade_list.append(trade)
					self.active_trade_obj[f"{exchange.name}_{strat_id}"]["TradeActive"] = True
					self.active_trade_obj[f"{exchange.name}_{strat_id}"]["buy"] = trade.buy
					self.active_trade_obj[f"{exchange.name}_{strat_id}"]["sell"] = trade.sell
					self.active_trade_obj[f"{exchange.name}_{strat_id}"]["expiration"] = None
				except:
					traceback.print_exc()
		for i in range(len(self.stop_trade_list)):
			try:
				if self.stop_trade_list[i]["trade"].trade_active:
					if self.stop_trade_list[i]["trade"].trade_complete() == True:
						exchange = self.stop_trade_list[i]["strat"]["exchanges"][0]
						pair = self.stop_trade_list[i]["strat"]["pair"]
						threshhold = self.stop_trade_list[i]["strat"]["threshhold"]
						trade_amount = self.stop_trade_list[i]["strat"]["alloc_of_total_balance"]
						self.stop_trade_list[i]["trade"] = StopClient(exchange, pair, threshhold, trade_amount)
				self.stop_trade_list[i]["trade"].do_trade()
			except:
				traceback.print_exc()
		print(datetime.datetime.now().isoformat())
		print(self.active_trade_obj)