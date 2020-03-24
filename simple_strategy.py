from exchanges import binance_api
from exchanges import kucoin_api
from exchanges.exchange_class import Exchange
from arb import arbitrage
import os
import random
import time



def main():
	binance = binance_api.bittrex_api(os.environ["BINANCE_SECRET"], os.environ["BINANCE_KEY"])
	kucoin = kucoin_api.kucoin_api(os.environ["KUCOIN_KEY"], os.environ["KUCOIN_SECRET"], os.environ["KUCOIN_PASSPHRASE"])
	exchange1 = Exchange("binance", binance)
	exchange2 = Exchange("kucoin", kucoin)
	pair1="XRP-USDT"
	pair2="XRP-USDT"
	threshhold = .01

	#init headers
	with open("log.txt", "a") as text_file:
			text_file.write("ts,priceDiff,margin,sell_exchange_name,buy_exchange_name,sell_pair,buy_pair,sell_price,buy_price,sell_amount,buy_amount,sell_margin,buy_margin,suggested_buy_amount,suggested_sell_amount,gross_margin,trade_decision\n")

	while True:
		price1 = exchange1.get_buy_price(pair1)
		price2 = exchange2.get_sell_price(pair2)
		# amount1 = amountList[random.randrange(len(amountList))]
		# amount2 = amountList[random.randrange(len(amountList))]
		rebalance = True


		a = arbitrage(exchange1, exchange2, pair1, pair2, amount1, amount2, price1, price2, threshhold=threshhold, get_amounts=True)
		sell_exchange_name, priceDiff, margin = a.get_opportunity(r=1)

		if sell_exchange_name != exchange2.name:
			a = arbitrage(exchange2, exchange1, pair2, pair1, amount2, amount1, threshhold=threshhold, run_op=True, get_amounts=True)
		if a.do_trade == True:
			print("executing")
			a.execute()
			while a.execution_complete() is not True:
				print("waiting for trades to complete")
				time.sleep(5)
			if rebalance == True:
				print("rebalancing")
				a.rebalance()
				while a.rebalance_complete() is not True:
					print("waiting for rebalance to complete")
					time.sleep(5)
			break
		time.sleep(5)

main()