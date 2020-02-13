class Trade:
	def __init__(self, exchange_1, amount_1, price_1, currency_1, order_type_1, identifier_1, exchange_2, amount_2, price_2, currency_2, order_type_2, identifier_2):
		self.data = {
			"1":{
				"exchange":exchange_1,
				"amount":amount_1,
				"price":price_1,
				"currency":currency_1,
				"order_type":order_type_1,
				"identifier":identifier_1
			}
			"2":{
				"exchange":exchange_2,
				"amount":amount_2,
				"price":price_2,
				"currency":currency_2,
				"order_type":order_type_2,
				"identifier":identifier_2
			}
		}

	def print_trade(self):
		print(self.data)

