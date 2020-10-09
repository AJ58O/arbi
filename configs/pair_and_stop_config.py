from exchanges.apis import binance_api
from exchanges.exchange_class import Exchange
from os import environ

def get_config():
	binance = binance_api.binance_api(environ["BINANCE_KEY"], environ["BINANCE_SECRET"])
	bina = Exchange("binance", binance)

	return {
		"hours_until_expiration":168,
		"stratList":[
			{
				"name":"simple_pair_trading",
				"id":"1",
				"threshhold":.01,
				"alloc_of_total_balance":.2,
				"pair":"XRP-USDT",
				"exchanges":[bina],
				"details":""
			},{
				"name":"simple_pair_trading",
				"id":"2",
				"threshhold":.05,
				"alloc_of_total_balance":.3,
				"pair":"XRP-USDT",
				"exchanges":[bina],
				"details":""
			},{
				"name":"simple_pair_trading",
				"id":"3",
				"threshhold":.09,
				"alloc_of_total_balance":.4,
				"pair":"XRP-USDT",
				"exchanges":[bina],
				"details":""
			},{
				"name":"stop_trading",
				"id":"4",
				"threshhold":.1,
				"alloc_of_total_balance":.9,
				"pair":"XRP-USDT",
				"exchanges":[bina],
				"details":""
			}
		]
	}