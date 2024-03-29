from exchanges.apis import binance_api
from exchanges.exchange_class import Exchange
from os import environ
from time import sleep
from time import time
from strategy.clients.paired_trade_client import paired_trade_client
from strategy.clients.stop_client import StopClient
from util.logger import logger
import datetime
import traceback
import sys



def main():
	sleepInterval = 120 #seconds
	logFileName=f"StrategyLogs_{str(time()).split('.')[0]}.txt"
	strat_logger = logger(logFileName,logFileName, logFileName)
	binance = binance_api.binance_api(environ["BINANCE_KEY"], environ["BINANCE_SECRET"])
	bina = Exchange("binance", binance)
	hours_until_expiration = 168

	# pair2="XRP-USDT"
	# pair3="XRP-USDT"
	# amountList = [50, 100, 300, 1000]

	strat1 = {
		"name":"simple_pair_trading",
		"id":"1",
		"threshhold":.005,
		"alloc_of_total_balance":.2,
		"pair":"XRP-USDT",
		"exchanges":[bina],
		"details":""
	}

	strat2 = {
		"name":"simple_pair_trading",
		"id":"2",
		"threshhold":.01,
		"alloc_of_total_balance":.3,
		"pair":"XRP-USDT",
		"exchanges":[bina],
		"details":""
	}

	strat3 = {
		"name":"simple_pair_trading",
		"id":"3",
		"threshhold":.02,
		"alloc_of_total_balance":.4,
		"pair":"XRP-USDT",
		"exchanges":[bina],
		"details":""
	}

	strat4 = {
		"name":"stop_trading",
		"id":"4",
		"threshhold":.07,
		"alloc_of_total_balance":.9,
		"pair":"XRP-USDT",
		"exchanges":[bina],
		"details":""
	}

	stratList = [strat1, strat2, strat4]
	active_trade_obj = {}
	paired_trade_list = []
	stop_trade_list = []


	for strat in stratList:
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
					paired_trade_list.append({"strat":strat,"trade":trade})
					active_trade_obj[f"{exchange.name}_{strat_id}"] = {}
					active_trade_obj[f"{exchange.name}_{strat_id}"]["TradeActive"] = True
					active_trade_obj[f"{exchange.name}_{strat_id}"]["buy"] = trade.buy
					active_trade_obj[f"{exchange.name}_{strat_id}"]["sell"] = trade.sell
					active_trade_obj[f"{exchange.name}_{strat_id}"]["expiration"] = None #set this only when we can determine a single trade has closed
					strat_logger.log(f"INITIALIZED SIMPLE TRADE: {trade.id}")

				except:
					strat_logger.log(f"ERROR INITIALIZING SIMPLE TRADE: {traceback.format_exc()}", error=True)
			elif name == "stop_trading":
				try:
					stop_trade = StopClient(exchange, pair, threshhold, trade_amount)
					stop_trade_list.append({"strat":strat, "trade":stop_trade})
					stop_trade.do_trade()
					strat_logger.log(f"INITIALIZED STOP TRADE: {stop_trade.id}")
				except:
					strat_logger.log(f"ERROR INITIALIZING STOP TRADE: {traceback.format_exc()}", error=True)

	sleep(sleepInterval)
	while True:
		for t in paired_trade_list:
			try:
				if t["trade"].trade_complete():
					strat_logger.log(f"COMPLETED SIMPLE TRADE: {t['trade'].id}")
					active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["TradeActive"] = False
					active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["buy"] = None
					active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["sell"] = None
					active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["expiration"] = None
					paired_trade_list.remove(t)
				elif t["trade"].only_one_trade_complete():
					strat_logger.log(f"ONLY ONE TRADE COMPLETE: {t['trade'].id}")
					if active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["expiration"] == None:
						active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["expiration"] = datetime.datetime.now() + datetime.timedelta(hours=hours_until_expiration)
					elif active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["expiration"] < datetime.datetime.now():
						strat_logger.log(f"EXPIRED OPEN SIMPLE TRADE, CANCELLING: {t['trade'].id}")
						t["trade"].cancel_open_trade()
						active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["TradeActive"] = False
						active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["buy"] = None
						active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["sell"] = None
						active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["expiration"] = None
						paired_trade_list.remove(t)
			except:
				strat_logger.log(f"ERROR EVALUATING SIMPLE PAIR: {traceback.format_exc()}", error=True)
		for key in active_trade_obj.keys():
			if active_trade_obj[key]["TradeActive"] == False:
				echanges = [ s["exchanges"] for s in stratList if s["id"] == key.split("_")[1] ][0]
				exchange = [e for e in exchanges if e.name in key][0]
				strat = [ s for s in stratList if s["id"] == key.split("_")[1] ][0]
				strat_id = strat.get("id")
				threshhold = strat.get("threshhold")
				pair = strat.get("pair")
				trade_amount = strat.get("alloc_of_total_balance")
				try:
					trade = paired_trade_client(exchange, pair, threshhold, trade_amount, run_trade=True)
					paired_trade_list.append(trade)
					active_trade_obj[f"{exchange.name}_{strat_id}"]["TradeActive"] = True
					active_trade_obj[f"{exchange.name}_{strat_id}"]["buy"] = trade.buy
					active_trade_obj[f"{exchange.name}_{strat_id}"]["sell"] = trade.sell
					active_trade_obj[f"{exchange.name}_{strat_id}"]["expiration"] = None
					strat_logger.log(f"NEW SIMPLE TRADE INITIALIZED: {trade.id}")
				except:
					strat_logger.log(f"ERROR INITIALIZING NEW SIMPLE PAIR: {traceback.format_exc()}", error=True)
		for i in range(len(stop_trade_list)):
			try:
				if stop_trade_list[i]["trade"].trade_active:
					print("STOP TRADE ACTIVE")
					if stop_trade_list[i]["trade"].trade_complete() == True:
						strat_logger.log(f"COMPLETED STOP TRADE: {stop_trade_list[i]['trade'].id}")
						exchange = stop_trade_list[i]["strat"]["exchanges"][0]
						pair = stop_trade_list[i]["strat"]["pair"]
						threshhold = stop_trade_list[i]["strat"]["threshhold"]
						trade_amount = stop_trade_list[i]["strat"]["alloc_of_total_balance"]
						stop_trade_list[i]["trade"] = StopClient(exchange, pair, threshhold, trade_amount)
						strat_logger.log(f"INITIALIZED NEW STOP TRADE: {stop_trade_list[i]['trade'].id}")
				stop_trade_list[i]["trade"].do_trade()
			except:
				strat_logger.log(f"ERROR EVALUATING STOP TRADE: {traceback.format_exc()}", error=True)
		print(datetime.datetime.now().isoformat())
		print(active_trade_obj)
		strat_logger.log(f"PAIRED STRAT STATE LOG:{active_trade_obj}")
		sleep(sleepInterval)

	



	




main()