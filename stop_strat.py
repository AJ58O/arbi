from exchanges import binance_api
from exchanges.exchange_class import Exchange
from os import environ
from time import sleep
from paired_trade_client import paired_trade_client
from stop_client import StopClient
import datetime
import traceback




def main():
	binance = binance_api.binance_api(environ["BINANCE_KEY"], environ["BINANCE_SECRET"])
	bina = Exchange("binance", binance)
	pair="XRP-USDT"
	threshhold = .01
	trade_amount = .99

	exchanges = [bina]
	# with open("stop_log.txt", "a") as text_file:
	# 	text_file.write(f"ts,exchange,pair,buy amount,buy price,sell amount,sell price,buy,sell,init_buy_bal,init_sell_bal,final_sell_bal,final_buy_bal\n")

	trade_list = []		
	for exchange in exchanges:
		try:
			trade = StopClient(exchange, pair, threshhold, trade_amount)			
			trade_list.append(trade)

		except:
			traceback.print_exc()
	sleep(5)
	while True:
		for t in trade_list:
			try:
				if t.trade_complete():
					active_trade_obj[t.exchange.name]["TradeActive"] = False
					active_trade_obj[exchange.name]["buy"] = None
					active_trade_obj[exchange.name]["sell"] = None
					trade_list.remove(t)
			except:
					traceback.print_exc()
		for key in active_trade_obj.keys():
			if active_trade_obj[key]["TradeActive"] == False:
				exchange = [e for e in exchanges if e.name == key][0]
				try:
					trade = paired_trade_client(exchange, pair, threshhold, trade_amount, run_trade=True)
					trade_list.append(trade)
					active_trade_obj[exchange.name]["TradeActive"] = True
					active_trade_obj[exchange.name]["buy"] = trade.buy
					active_trade_obj[exchange.name]["sell"] = trade.sell
				except:
					traceback.print_exc()
		print(datetime.datetime.now().isoformat())
		print(active_trade_obj)
		sleep(5)

	



	




main()