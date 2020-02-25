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
	
	exchange1 = Exchange("kucoin", kucoin)
	exchange2 = Exchange("binance", binance)
	
	pair1="XRP-USDT"
	pair2="XRP-USDT"
	pair3="XRP-USDT"
	# amountList = [50, 100, 300, 1000]
	threshhold = .01
	rebalance = True

	#init headers
	with open("log.txt", "a") as text_file:
			text_file.write("ts,priceDiff,margin,sell_exchange_name,buy_exchange_name,sell_pair,buy_pair,sell_price,buy_price,sell_amount,buy_amount,sell_margin,buy_margin,suggested_buy_amount,suggested_sell_amount,gross_margin,trade_decision\n")

	while True:
		a = arbitrage(exchange1, exchange2, pair1, pair2, threshhold=threshhold, run_op=True, get_amounts=True)
		if a.sell_exchange.name != exchange2.name:
			a = arbitrage(exchange2, exchange1, pair2, pair1, threshhold=threshhold, run_op=True, get_amounts=True)
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