from exchanges import binance_api, bittrex_api, bitrue_api, coinbase_api, kucoin_api, exchange_class
import os
import json

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



# e_list = [kucoin, binance, bittrex, bitrue, coinbase]
# e_name_list = ["kucoin", "binance", "bittrex", "bitrue", "coinbase"]

e_list = [binance]
e_name_list = ["binance"]


# for order in kucoin.get_open_orders("XRP-USDT")["items"]:
# 	print(kucoin.cancel("XRP-USDT",order["id"]))
# for order in binance.get_open_orders("XRP-USDT"):
# 	print(binance.cancel("XRP-USDT",order["orderId"]))
# for order in bittrex.get_open_orders("XRP-USDT")["result"]:
# 	print(order)
# 	print("cancelling right now")
# 	print(bittrex.cancel("XRP-USDT",order["OrderUuid"]))


# trade_list = {
# 	"bittrex": {
# 		"buy":"b9366578-6220-4dd4-b02d-8a318c74e88e",
# 		"sell":"881ba5cf-84d3-48fe-b445-3f7c931c86ff"
# 	},
# 	"binance": {
# 		"buy":"459581489",
# 		"sell":"459581498"
# 	},
# 	"kucoin": {
# 		"buy":"5e5af166cc9d29000acff631",
# 		"sell":"5e5af1675c7a21000a30e39f"
# 	}
# }
# for e in range(len(e_list)):
# 	with open(f"{e_name_list[e]}_active_trade.txt", "w") as text_file:
# 		text_file.write(json.dumps({
# 				"buy_price":"buy_price",
# 				"buy_amount":"buy_amount",
# 				"buy":trade_list[e_name_list[e]]["buy"],
# 				"sell_price":"sell_price",
# 				"sell_amount":"sell_amount",
# 				"sell":trade_list[e_name_list[e]]["sell"],
# 				"init_buy_bal":"init_buy_bal",
# 				"init_sell_bal":"init_sell_bal"
# 			}))



print("getting buy prices")
for i in range(len(e_list)):
	try:
		print(f"getting buy price for {e_name_list[i]}")
		print(e_list[i].get_buy_price("XRP-USDT"))
	except Exception as e:
		print(e)

print("getting sell prices")
for i in range(len(e_list)):
	try:
		print(f"getting sell price for {e_name_list[i]}")
		print(e_list[i].get_sell_price("XRP-USDT"))
	except Exception as e:
		print(e)

print("getting open orders")
for i in range(len(e_list)):
	try:
		print(f"getting open orders for {e_name_list[i]}")
		print(e_list[i].get_open_orders("XRP-USDT"))
	except Exception as e:
		print(e)
# # print("showing wallet")
# for i in range(len(e_list)):
# 	try:
# # 		print(f"wallet for {e_name_list[i]}")
# # 		print(e_list[i].wallet)
# # 	except Exception as e:
# # 		print(e)
print("getting getting balances")
for i in range(len(e_list)):
	try:
		print(f"getting balance for {e_name_list[i]}")
		print(e_list[i].get_balance("XRP"))
	except Exception as e:
		print(e)

print("getting getting balances")
for i in range(len(e_list)):
	try:
		print(f"getting balance for {e_name_list[i]}")
		print(e_list[i].get_balance("USDT"))
	except Exception as e:
		print(e)

# # print("making buy orders")
# for i in range(len(e_list)):
# 	try:
# 		print(f"placing buy for {e_name_list[i]}")
# 		print(e_list[i].buy("XRP-USDT", 555, .236))
# 	except Exception as e:
# # 		print(e)

# print("making sell orders")
# for i in range(len(e_list)):
# 	try:
# 		print(f"placing sell for {e_name_list[i]}")
# 		print(e_list[i].sell("XRP-USDT", 90, .155))
# 	except Exception as e:
# 		print(e)



# print("order completes")
# for i in range(len(e_list)):
# 	try:
# 		print(f"order complete for {e_name_list[i]}")
# 		print(e_list[i].order_complete("488933603", "XRP-USD"))
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
# # print(binance.wallet)
# for i in range(len(e_list)):
# 	try:
# 		# print(kucoin.e.client.create_deposit_address("USDT", chain="TRC20"))
# 		print(e_list[i].send_tx("XRP", 555, binance.wallet["XRP"]["address"], memo=binance.wallet["XRP"]["memo"]))
# 	except Exception as e:
# 		print(e)

