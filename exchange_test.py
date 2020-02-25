from exchanges import binance_api, bittrex_api, bitrue_api, coinbase_api, kucoin_api, exchange_class
import os

print("initializing exchanges")
try:
	print("initializing binance")
	binance = exchange_class.Exchange("binance", binance_api.binance_api(os.environ["BINANCE_KEY"], os.environ["BINANCE_SECRET"]))
except Exception as e:
	print(e)
try:
	print("initializing bittrex")
	bittrex = exchange_class.Exchange("bittrex", bittrex_api.bittrex_api(os.environ["BITTREX_SECRET"], os.environ["BITTREX_KEY"]))
except Exception as e:
	print(e)
try:	
	print("initializing bitrue")
	bitrue = exchange_class.Exchange("bitrue", bitrue_api.bitrue_api(os.environ["BITRUE_KEY"], os.environ["BITRUE_SECRET"]))
except Exception as e:
	print(e)
try:
	print("initializing coinbase")
	coinbase = exchange_class.Exchange("coinbase", coinbase_api.coinbase_api(os.environ["CB_SECRET"], os.environ["CB_KEY"], os.environ["CB_PASSPHRASE"]))
except Exception as e:
	print(e)

try:
	print("initializing kucoin")
	kucoin = exchange_class.Exchange("kucoin", kucoin_api.kucoin_api(os.environ["KUCOIN_KEY"], os.environ["KUCOIN_SECRET"], os.environ["KUCOIN_PASSPHRASE"]))
except Exception as e:
	print(e)


binance = exchange_class.Exchange("binance", binance_api.binance_api(os.environ["BINANCE_KEY"], os.environ["BINANCE_SECRET"]))

# e_list = [kucoin, binance, bittrex, bitrue, coinbase]
# e_name_list = ["kucoin", "binance", "bittrex", "bitrue", "coinbase"]

e_list = [kucoin]
e_name_list = ["kucoin"]



# print("getting buy prices")
# for i in range(len(e_list)):
# 	try:
# 		print(f"getting buy price for {e_name_list[i]}")
# 		print(e_list[i].get_buy_price("XRP-BTC"))
# 	except Exception as e:
# 		print(e)

# print("getting sell prices")
# for i in range(len(e_list)):
# 	try:
# 		print(f"getting sell price for {e_name_list[i]}")
# 		print(e_list[i].get_sell_price("XRP-USDT"))
# 	except Exception as e:
# 		print(e)
# print("showing wallet")
# for i in range(len(e_list)):
# 	try:
# 		print(f"wallet for {e_name_list[i]}")
# 		print(e_list[i].wallet)
# 	except Exception as e:
# 		print(e)
# print("getting getting balances")
# for i in range(len(e_list)):
# 	try:
# 		print(f"getting balance for {e_name_list[i]}")
# 		print(e_list[i].get_balance("XRP"))
# 	except Exception as e:
# 		print(e)

# print("getting getting balances")
# for i in range(len(e_list)):
# 	try:
# 		print(f"getting balance for {e_name_list[i]}")
# 		print(e_list[i].get_balance("USDT"))
# 	except Exception as e:
# 		print(e)

# print("making buy orders")
# for i in range(len(e_list)):
# 	try:
# 		print(f"placing buy for {e_name_list[i]}")
# 		print(e_list[i].buy("XRP-USDT", 20, .25))
# 	except Exception as e:
# 		print(e)

# print("making sell orders")
# for i in range(len(e_list)):
# 	try:
# 		print(f"placing sell for {e_name_list[i]}")
# 		print(e_list[i].sell("XRP-USDT", 250, .2656))
# 	except Exception as e:
# 		print(e)



# print("order completes")
# for i in range(len(e_list)):
# 	try:
# 		print(f"order complete for {e_name_list[i]}")
# 		print(e_list[i].order_complete("234", "XRP-USD"))
# 	except Exception as e:
# 		print(e)

# print("send txns")
# for i in range(len(e_list)):
# 	try:
# 		print(f"sending tx from {e_name_list[i]}")
# 		print(binance.wallet["USDT"]["address"])
# 		print(e_list[i].send_tx("USDT", 5, binance.wallet["USDT"]["address"]))
# 	except Exception as e:
# 		print(e)

# for i in range(len(e_list)):
# 	try:
# 		# print(kucoin.e.client.create_deposit_address("USDT", chain="TRC20"))
# 		print(e_list[i].send_tx("XRP", 21, bittrex.wallet["XRP"]["address"], memo=bittrex.wallet["XRP"]["memo"]))
# 	except Exception as e:
# 		print(e)

