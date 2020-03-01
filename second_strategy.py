from exchanges import bittrex_api, coinbase_api, binance_api, bitrue_api, kucoin_api
from exchanges.exchange_class import Exchange
from arb import arbitrage
from os import environ
from time import sleep



def main():
	bittrex = bittrex_api.bittrex_api(environ["BITTREX_SECRET"], environ["BITTREX_KEY"])
	coinbase = coinbase_api.coinbase_api(environ["CB_SECRET"], environ["CB_KEY"], environ["CB_PASSPHRASE"])
	binance = binance_api.binance_api(environ["BINANCE_KEY"], environ["BINANCE_SECRET"])
	bitrue = bitrue_api.bitrue_api(environ["BITRUE_KEY"], environ["BITRUE_SECRET"])
	kucoin = kucoin_api.kucoin_api(environ["KUCOIN_KEY"], environ["KUCOIN_SECRET"], environ["KUCOIN_PASSPHRASE"])
	exchange1 = Exchange("bittrex", bittrex)
	exchange2 = Exchange("binance", binance)
	exchange3 = Exchange("kucoin", kucoin)
	pair1="XRP-USDT"
	pair2="XRP-USDT"
	pair3="XRP-USDT"
	# amountList = [50, 100, 300, 1000]
	threshhold = .01

	#init headers
	with open("log.txt", "a") as text_file:
			text_file.write("ts,priceDiff,margin,sell_exchange_name,buy_exchange_name,sell_pair,buy_pair,sell_price,buy_price,sell_amount,buy_amount,sell_margin,buy_margin,suggested_buy_amount,suggested_sell_amount,gross_margin,trade_decision\n")

	while True:
		price1 = exchange1.get_buy_price(pair1)
		price2 = exchange2.get_sell_price(pair2)
		price3 = exchange3.get_sell_price(pair3)
		# amount1 = amountList[random.randrange(len(amountList))]
		# amount2 = amountList[random.randrange(len(amountList))]
		rebalance = False

		a = arbitrage(exchange1, exchange2, pair1, pair2, price1, price2, threshhold=threshhold, run_op=True, get_amounts=True)
		try:
			if a.sell_exchange.name != exchange2.name:
				a = arbitrage(exchange2, exchange1, pair2, pair1, threshhold=threshhold, run_op=True, get_amounts=True)
				if a.do_trade == True:
					print("executing")
					a.execute()
					while a.execution_complete() is not True:
						sleep(5)
					if rebalance == True:
						print("rebalancing")
						a.rebalance()
						while a.rebalance_complete() is not True:
							sleep(5)
		except Exception as e:
			print(e)
		sleep(2)
		b = arbitrage(exchange1, exchange3, pair1, pair3, price1, price3, threshhold=threshhold, run_op=True, get_amounts=True)
		try:
			if b.sell_exchange.name != exchange3.name:
				b = arbitrage(exchange3, exchange1, pair3, pair1, threshhold=threshhold, run_op=True, get_amounts=True)
				if b.do_trade == True:
					print("executing")
					b.execute()
					while b.execution_complete() is not True:
						sleep(5)
					if rebalance == True:
						print("rebalancing")
						b.rebalance()
						while b.rebalance_complete() is not True:
							sleep(5)
		except Exception as e:
			print(e)
		sleep(2)
		c = arbitrage(exchange2, exchange3, pair2, pair3, price2, price3, threshhold=threshhold, run_op=True, get_amounts=True)
		try:
			if c.sell_exchange.name != exchange3.name:
				c = arbitrage(exchange3, exchange2, pair3, pair2, threshhold=threshhold, run_op=True, get_amounts=True)
				if c.do_trade == True:
					print("executing")
					c.execute()
					while c.execution_complete() is not True:
						sleep(5)
					if rebalance == True:
						print("rebalancing")
						c.rebalance()
						while c.rebalance_complete() is not True:
							sleep(5)
		except Exception as e:
			print(e)
		sleep(5)

main()