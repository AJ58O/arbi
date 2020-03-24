import datetime
import json
import traceback

class unpaired_trading_client:
	def __init__(self, exchange, pair, threshhold, trade_amount, side, amount=None, price=None, run_trade=False, regen=False, log_suffix=""):
		self.exchange = exchange
		self.suffix = log_suffix
		self.pair = pair
		self.threshhold = threshhold
		self.trade_amount = trade_amount
		self.side = side
		self.sell_cur = self.pair.split("-")[0]
		self.buy_cur = self.pair.split("-")[1]
		self.cur = self.sell_cur if side == "sell" else self.buy_cur
		print(f"exchange: {self.exchange.name}")
		if regen == True:
			try:
				self.regenerate_active_trade()
				return None
			except:
				traceback.print_exc()
		if run_trade == True:
			if price == None:
				self.get_prices()
			else:
				if side == "buy":
					self.buy_price = price
					self.price = price
					self.sell_price = None
				elif side == "sell":
					self.sell_price = price
					self.price = price
					self.buy_price = None
			self.get_amounts()
			if amount != None:
				if side == "buy":
					self.buy_amount = amount
				elif side == "sell":
					self.sell_amount = amount

			self.execute_trade()
		print("trade initialized")


	def get_amounts(self):
		self.init_sell_bal, self.init_buy_bal = self.get_balances()
		self.unbal_buy_amount = round(self.trade_amount * float(self.init_buy_bal), 1)
		self.unbal_sell_amount = round(self.trade_amount * float(self.init_sell_bal), 1)
		self.buy_amount = min(round((self.unbal_buy_amount/self.sell_price+self.unbal_sell_amount)/2, 1), self.unbal_buy_amount/self.sell_price)
		self.sell_amount = min(round((self.unbal_buy_amount/self.buy_price+self.unbal_sell_amount)/2, 1), self.unbal_sell_amount)
		print(f"BuyAmount: {self.buy_amount}")
		print(f"SellAmount: {self.sell_amount}")
		return self.buy_amount, self.sell_amount

	def get_next_amount(self):
		if self.side == "sell":
			return round((self.sell_amount * self.sell_price) * .98, 1)
		elif self.side == "buy":
			return round((self.buy_amount / self.buy_price) * .98, 1)

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
		if self.side == "buy":
			self.buy = self.exchange.buy(self.pair, buy_amount, buy_price)
			self.sell = None
		elif self.side == "sell":
			self.sell = self.exchange.sell(self.pair, sell_amount, sell_price)
			self.buy = None
		print(f"buy: {self.buy}")
		print(f"sell: {self.sell}")
		self.log_active_trade()
		return self.buy, self.sell

	def get_active_trade(self):
		with open(f"{self.exchange.name}_active_trade{self.suffix}.txt") as json_file:
			data = json.loads(json_file.read())
		return data

	def log_active_trade(self):
		with open(f"{self.exchange.name}_active_trade{self.suffix}.txt", "w") as text_file:
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
		with open(f"{self.exchange.name}_active_trade{self.suffix}.txt", "w") as text_file:
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

	def get_trade_price(self):
		if self.side == "buy":
			return self.buy_price
		elif self.side == "sell":
			return self.sell_price

	def get_next_trade_price(self):
		if self.side == "buy":
			return self.buy_price + self.buy_price * self.threshhold
		elif self.side == "sell":
			return self.sell_price - self.sell_price * self.threshhold

	def cancel_trade(self):
		if self.side == "buy":
			self.exchange.cancel(self.pair, self.buy)
		elif self.side == "sell"
			self.exchange.cancel(self.pair, self.sell)

	def trade_complete(self):
		if self.side == "buy":
			self.buy_complete = self.exchange.order_complete(self.buy, self.pair) 
			self.sell_complete = None

		elif self.side == "sell":
			self.sell_complete = self.exchange.order_complete(self.sell, self.pair)
			self.buy_complete = None

		print(f"buy_complete: {self.buy_complete}")
		print(f"sell_complete: {self.sell_complete}")
		if self.buy_complete == True or self.sell_complete == True:
			self.final_sell_bal, self.final_buy_bal = self.get_balances()
			self.log_everything()
			self.clear_active_trade_log()
			return True
		return False
