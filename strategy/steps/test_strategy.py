from exchanges.apis import binance_api
from exchanges.exchange_class import Exchange
from os import environ
from time import sleep
from strategy.clients.paired_trade_client import paired_trade_client
from strategy.clients.stop_client import StopClient
import datetime
import traceback
import sys



def main():
	binance = binance_api.binance_api(environ["BINANCE_KEY"], environ["BINANCE_SECRET"])
	bina = Exchange("binance", binance)
	hours_until_expiration = 168

	# pair2="XRP-USDT"
	# pair3="XRP-USDT"
	# amountList = [50, 100, 300, 1000]

	strat1 = {
		"name":"simple_pair_trading",
		"id":"1",
		"threshhold":.01,
		"alloc_of_total_balance":.2,
		"pair":"XRP-USDT",
		"exchanges":[bina],
		"details":""
	}

	strat2 = {
		"name":"simple_pair_trading",
		"id":"2",
		"threshhold":.05,
		"alloc_of_total_balance":.3,
		"pair":"XRP-USDT",
		"exchanges":[bina],
		"details":""
	}

	strat3 = {
		"name":"simple_pair_trading",
		"id":"3",
		"threshhold":.09,
		"alloc_of_total_balance":.4,
		"pair":"XRP-USDT",
		"exchanges":[bina],
		"details":""
	}

	strat4 = {
		"name":"stop_trading",
		"id":"4",
		"threshhold":.1,
		"alloc_of_total_balance":.9,
		"pair":"XRP-USDT",
		"exchanges":[bina],
		"details":""
	}

	stratList = [strat1, strat2, strat3, strat4]
	active_trade_obj = {}
	with open("trade_log.txt", "a") as text_file:
		text_file.write(f"ts,exchange,pair,buy amount,buy price,sell amount,sell price,buy,sell,init_buy_bal,init_sell_bal,final_sell_bal,final_buy_bal\n")

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
				except:
					traceback.print_exc()
			elif name == "stop_trading":
				try:
					stop_trade = StopClient(exchange, pair, threshhold, trade_amount)
					stop_trade_list.append({"strat":strat, "trade":stop_trade})
					stop_trade.do_trade()
				except:
					traceback.print_exc()

	sleep(5)
	while True:
		for t in paired_trade_list:
			try:
				if t["trade"].trade_complete():
					active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["TradeActive"] = False
					active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["buy"] = None
					active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["sell"] = None
					active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["expiration"] = None
					t["trade"] = None
				elif t["trade"].only_one_trade_complete():
					if active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["expiration"] == None:
						active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["expiration"] = datetime.datetime.now() + datetime.timedelta(hours=hours_until_expiration)
					elif active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["expiration"] < datetime.datetime.now():
						t["trade"].cancel_open_trade()
						active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["TradeActive"] = False
						active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["buy"] = None
						active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["sell"] = None
						active_trade_obj[f"{t['trade'].exchange.name}_{t['strat']['id']}"]["expiration"] = None
						t["trade"] = None
			except:
					traceback.print_exc()
		for key in active_trade_obj.keys():
			if active_trade_obj[key]["TradeActive"] == False:
				echanges = [ s["exchanges"] for s in stratList if s["id"] == key.split("_")[1] ][0]
				exchange = [e for e in exchanges if e.name in key][0]
				strat = [s for s in paired_trade_list if s["trade"] == None][0]
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
				except:
					traceback.print_exc()
		for i in range(len(stop_trade_list)):
			try:
				if stop_trade_list[i]["trade"].trade_active:
					if stop_trade_list[i]["trade"].trade_complete() == True:
						exchange = stop_trade_list[i]["strat"]["exchanges"][0]
						pair = stop_trade_list[i]["strat"]["pair"]
						threshhold = stop_trade_list[i]["strat"]["threshhold"]
						trade_amount = stop_trade_list[i]["strat"]["alloc_of_total_balance"]
						stop_trade_list[i]["trade"] = StopClient(exchange, pair, threshhold, trade_amount)
				stop_trade_list[i]["trade"].do_trade()
			except:
				traceback.print_exc()
		print(datetime.datetime.now().isoformat())
		print(active_trade_obj)
		sleep(10)

	



	




main()