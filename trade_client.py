import datetime
import json
import traceback

class trade_client:
	def __init__(self, exchange, pair, threshhold, trade_amount, run_trade=False, regen=False):
		self.exchange = exchange
		self.pair = pair
		self.threshhold = threshhold
		self.trade_amount = trade_amount
		self.sell_cur = self.pair.split("-")[0]
		self.buy_cur = self.pair.split("-")[1]
		print(f"exchange: {self.exchange.name}")
		if regen == True:
			try:
				self.regenerate_active_trade()
				return None
			except:
				traceback.print_exc()
		if run_trade == True:
			self.get_amounts()
			self.get_prices()
			self.execute_trade()
		print("trade initialized")


	def get_amounts(self):
		self.init_sell_bal, self.init_buy_bal = self.get_balances()
		self.buy_amount = round(self.trade_amount * float(self.init_buy_bal), 1)
		self.sell_amount = round(self.trade_amount * float(self.init_sell_bal), 1)
		print(f"BuyAmount: {self.buy_amount}")
		print(f"SellAmount: {self.sell_amount}")
		return self.buy_amount, self.sell_amount

	def get_balances(self):
		sell_cur_bal = self.exchange.get_balance(self.sell_cur)
		buy_cur_bal = self.exchange.get_balance(self.buy_cur)
		return sell_cur_bal, buy_cur_bal


	def get_prices(self):
		self.price =(float(self.exchange.get_buy_price(self.pair)) + float(self.exchange.get_sell_price(self.pair)))/2
		self.buy_price = round(self.price - (self.threshhold * self.price), 3)
		self.sell_price = round(self.price + (self.threshhold * self.price), 3)
		print(f"buy_price: {self.buy_price}")
		print(f"sell_price: {self.sell_price}")
		print(f"price: {self.price}")
		return self.buy_price, self.sell_price

	def execute_trade(self, buy_price=None, sell_price=None, buy_amount=None, sell_amount=None):
		if buy_price == None:
			buy_price = self.buy_price
		if sell_price == None:
			sell_price = self.sell_price
		if buy_amount == None:
			buy_amount = self.buy_amount
		if sell_amount == None:
			sell_amount = self.sell_amount
		self.buy = self.exchange.buy(self.pair, buy_amount, buy_price)
		self.sell = self.exchange.sell(self.pair, sell_amount, sell_price)
		print(f"buy: {self.buy}")
		print(f"sell: {self.sell}")
		self.log_active_trade()
		return self.buy, self.sell

	def get_active_trade(self):
		with open(f"{self.exchange.name}_active_trade.txt") as json_file:
			data = json.loads(json_file.read())
		return data

	def log_active_trade(self):
		with open(f"{self.exchange.name}_active_trade.txt", "w") as text_file:
			text_file.write(json.dumps({
					"buy_price":self.buy_price,
					"buy_amount":self.buy_amount,
					"buy":self.buy,
					"sell_price":self.sell_price,
					"sell_amount":self.sell_amount,
					"sell":self.sell,
					"init_buy_bal":self.init_buy_bal,
					"init_sell_bal":self.init_sell_bal
				}))

	def clear_active_trade_log(self):
		with open(f"{self.exchange.name}_active_trade.txt", "w") as text_file:
			text_file.write("")

	def regenerate_active_trade(self):
		active_trade = self.get_active_trade()
		self.buy_price = active_trade["buy_price"]
		self.buy_amount = active_trade["buy_amount"]
		self.buy = active_trade["buy"]
		self.sell_price = active_trade["sell_price"]
		self.sell_amount = active_trade["sell_amount"]
		self.sell = active_trade["sell"]
		self.init_buy_bal = active_trade["init_buy_bal"]
		self.init_sell_bal = active_trade["init_sell_bal"]

	def log_everything(self):
		with open("trade_log.txt", "a") as text_file:
			text_file.write(f"{datetime.datetime.now().isoformat()},{self.exchange.name},{self.pair},{self.buy_amount},{self.buy_price},{self.sell_amount},{self.sell_price},{self.buy},{self.sell},{self.init_buy_bal},{self.init_sell_bal},{self.final_sell_bal},{self.final_buy_bal}\n")

	def trade_complete(self):
		self.buy_complete = self.exchange.order_complete(self.buy, self.pair) 
		self.sell_complete = self.exchange.order_complete(self.sell, self.pair)
		print(f"buy_complete: {self.buy_complete}")
		print(f"sell_complete: {self.sell_complete}")
		if self.buy_complete and self.sell_complete:
			self.final_sell_bal, self.final_buy_bal = self.get_balances()
			self.log_everything()
			self.clear_active_trade_log()
			return True
		return False