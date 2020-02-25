from exchanges import bittrex_api
from exchanges import coinbase_api
from exchanges import binance_api
from exchanges import bitrue_api
from exchanges.exchange_class import Exchange
from arb import arbitrage
import os
import random
import time



def main():
	bittrex = bittrex_api.bittrex_api(os.environ["BITTREX_SECRET"], os.environ["BITTREX_KEY"])
	coinbase = coinbase_api.coinbase_api(os.environ["CB_SECRET"], os.environ["CB_KEY"], os.environ["CB_PASSPHRASE"])
	binance = binance_api.binance_api(os.environ["BINANCE_KEY"], os.environ["BINANCE_SECRET"])
	bitrue = bitrue_api.bitrue_api(os.environ["BITRUE_KEY"], os.environ["BITRUE_SECRET"])
	exchange1 = Exchange("bittrex", bittrex)
	exchange2 = Exchange("binance", binance)
	pair1="XRP-USDT"
	pair2="XRP-USDT"
	# amountList = [50, 100, 300, 1000]
	threshhold = .01

	#init headers
	with open("log.txt", "a") as text_file:
			text_file.write("ts,priceDiff,margin,sell_exchange_name,buy_exchange_name,sell_pair,buy_pair,sell_price,buy_price,sell_amount,buy_amount,sell_margin,buy_margin,suggested_buy_amount,suggested_sell_amount,gross_margin,trade_decision\n")

	while True:
		price1 = exchange1.get_buy_price(pair1)
		price2 = exchange2.get_sell_price(pair2)
		# amount1 = amountList[random.randrange(len(amountList))]
		# amount2 = amountList[random.randrange(len(amountList))]
		rebalance = False
		get_amounts = True
		run_op = True


		a = arbitrage(exchange1, exchange2, pair1, pair2, price1, price2, threshhold=threshhold, run_op=run_op, get_amounts=get_amounts)
		try:
			if a.sell_exchange.name != exchange2.name:
				a = arbitrage(exchange2, exchange1, pair2, pair1, threshhold=threshhold, run_op=run_op, get_amounts=get_amounts)
		except Exception as e:
			print(e)
		# if a.do_trade == True:
		# 	a.execute()
		# 	while a.execution_complete() is not True:
		# 		time.sleep(5)
		# 	if rebalance == True;
		# 		a.rebalance()
		# 		while a.rebalance_complete() is not True:
		# 			time.sleep(5)
		# 	break
		time.sleep(5)

main()