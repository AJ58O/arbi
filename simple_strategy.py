from arb import arbitrage



def main():
	bittrex = bittrex_api.Bittrex(os.environ["BITTREX_SECRET"], os.environ["BITTREX_KEY"])
	coinbase = coinbase_api.CB(os.environ["CB_SECRET"], os.environ["CB_KEY"], os.environ["CB_PASSPHRASE"])
	exchange1 = Exchange("bittrex", bittrex)
	exchange2 = Exchange("coinbase", coinbase)
	pair1="BTC-XRP"
	pair2="XRP-BTC"
	amountList = [50, 100, 300, 1000]
	amount1=50
	amount2=300
	threshold = .012

	#init headers
	with open("log.txt", "a") as text_file:
			text_file.write("ts,priceDiff,margin,sell_exchange_name,buy_exchange_name,sell_pair,buy_pair,sell_price,buy_price,sell_amount,buy_amount,sell_margin,buy_margin,suggested_buy_amount,suggested_sell_amount,gross_margin,trade_decision\n")

	while True:
		price1 = exchange1.get_buy_price(pair1)
		price2 = exchange2.get_sell_price(pair2)
		amount1 = amountList[random.randrange(len(amountList))]
		amount2 = amountList[random.randrange(len(amountList))]


		a = arbitrage(exchange1, exchange2, pair1, pair2, amount1, amount2, price1, price2, threshhold=threshhold)
		sell_exchange_name, priceDiff, margin = a.get_opportunity(r=1)

		if sell_exchange_name != exchange2.name:
			a = arbitrage(exchange2, exchange1, pair2, pair1, amount2, amount1, threshhold=threshhold, run_op=True)
			if a.do_trade == True:
				a.execute()
				a.rebalance()
				while a.rebalance_complete() is not True:
					time.sleep(5)

		# 500 * x = margin

		time.sleep(5)


main()