from exchanges import bittrex_api, coinbase_api, binance_api, bitrue_api, kucoin_api
from exchanges.exchange_class import Exchange
from arb import arbitrage
from os import environ
from time import sleep
from unpaired_trading_client import unpaired_trading_client
import datetime
import traceback




def main():
	bittrex = bittrex_api.bittrex_api(environ["BITTREX_SECRET"], environ["BITTREX_KEY"])
	coinbase = coinbase_api.coinbase_api(environ["CB_SECRET"], environ["CB_KEY"], environ["CB_PASSPHRASE"])
	binance = binance_api.binance_api(environ["BINANCE_KEY"], environ["BINANCE_SECRET"])
	bitrue = bitrue_api.bitrue_api(environ["BITRUE_KEY"], environ["BITRUE_SECRET"])
	kucoin = kucoin_api.kucoin_api(environ["KUCOIN_KEY"], environ["KUCOIN_SECRET"], environ["KUCOIN_PASSPHRASE"])
	bitt = Exchange("bittrex", bittrex)
	bina = Exchange("binance", binance)
	kuco = Exchange("kucoin", kucoin)
	pair="XRP-USDT"
	# pair2="XRP-USDT"
	# pair3="XRP-USDT"
	# amountList = [50, 100, 300, 1000]
	threshhold_list = [.01, .02, .03]
	trade_amount_list = [.2, .1, .05]

	exchanges = [bitt, bina, kuco]
	with open("trade_log.txt", "a") as text_file:
		text_file.write(f"ts,exchange,pair,buy amount,buy price,sell amount,sell price,buy,sell,init_buy_bal,init_sell_bal,final_sell_bal,final_buy_bal\n")

	trade_list = []		
	for exchange in exchanges:
		active_trade_obj[exchange.name] = {}
		for i in range(len(threshhold_list)):
			try:
				threshhold = threshhold_list[i]
				trade_amount = trade_amount_list[i]
				buy = unpaired_trading_client(exchange, pair, threshhold, trade_amount, "buy", run_trade=True, log_suffix=f"_{threshhold}_buy")
				trade_list.append(buy)
				sell = unpaired_trading_client(exchange, pair, threshhold, trade_amount, "sell", run_trade=True, log_suffix=f"_{threshhold}_sell")
				trade_list.append(sell)

			except:
				traceback.print_exc()
		sleep(2)
	sleep(3)
	while True:
		for t in trade_list:
			try:
				if t.trade_complete():
					try:
						opposing_trade = [tr for tr in trade_list if tr.exchange.name == t.exchange.name and tr.threshhold == t.threshhold and tr.side != t.side][0]
						opposing_trade.cancel_trade()
						new_trade = unpaired_trading_client(t.exchange, t.pair, t.threshhold, t.trade_amount, opposing_trade.side, amount=t.get_next_amount(), price=t.get_next_trade_price(), run_trade=True, log_suffix=f"_{t.threshhold}_{opposing_trade.side}")
						trade_list.append(new_trade)
						trade_list.remove(t)
						trade_list.remove(opposing_trade)
					except:
						side = "sell" if t.side == "buy" else "buy"
						new_trade = unpaired_trading_client(t.exchange, t.pair, t.threshhold, t.trade_amount, side, amount=t.get_next_amount(), price=t.get_next_trade_price(), run_trade=True, log_suffix=f"_{t.threshhold}_{side}")
						trade_list.append(new_trade)
						trade_list.remove(t)
			except:
					traceback.print_exc()

			sleep(2)
		print(datetime.datetime.now().isoformat())
		sleep(3)

	



	




main()