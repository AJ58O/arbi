import datetime
import json
import traceback
from util.logger import logger
import uuid

class paired_trade_client:
	def __init__(self, exchange, pair, threshhold, trade_amount, run_trade=False, regen=False, log_suffix="", trade_id=None):
		self.exchange = exchange
		self.suffix = log_suffix
		self.pair = pair
		self.threshhold = threshhold
		self.trade_amount = trade_amount
		self.sell_cur = self.pair.split("-")[0]
		self.buy_cur = self.pair.split("-")[1]
		self.id = trade_id if trade_id is not None else str(uuid.uuid1())
		self.logger = logger(f"STATE_paired_trade_{self.id}", f"LOGS_paired_trade_{self.id}", f"LOGS_paired_trade_{self.id}")
		print(f"exchange: {self.exchange.name}")
		if regen == True:
			try:
				self.regenerate_active_trade()
				return None
			except:
				e = traceback.format_exc()
				self.logger.log(f"ERROR REGENERATING: {e}")


		if run_trade == True:
			self.get_prices()
			self.get_amounts()
			self.execute_trade()
		self.logger.log(f"trade initialized: {self.id}")

	def get_amounts(self):
		self.init_sell_bal, self.init_buy_bal = self.get_balances()
		self.unbal_buy_amount = round(self.trade_amount * float(self.init_buy_bal), 1)
		self.unbal_sell_amount = round(self.trade_amount * float(self.init_sell_bal), 1)
		self.buy_amount = min(round((self.unbal_buy_amount/self.sell_price+self.unbal_sell_amount)/2, 1), round(self.unbal_buy_amount/self.sell_price, 1))
		self.sell_amount = min(round((self.unbal_buy_amount/self.buy_price+self.unbal_sell_amount)/2, 1), round(self.unbal_sell_amount, 1))
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
		self.logger.log(f"trades executed. buy: {self.buy} sell: {self.sell}")
		state_log = json.dumps({
			"exchange":self.exchange.name,
			"pair":self.pair,
			"threshhold":self.threshhold,
			"buy_amount":buy_amount,
			"sell_amount":sell_amount,
			"init_buy_bal":self.init_buy_bal,
			"init_sell_bal":self.init_sell_bal,
			"sell_cur":self.sell_cur,
			"buy_cur":self.buy_cur,
			"sell":self.sell,
			"buy":self.buy,
			"id":self.id
		})
		self.logger.log(f"PAIR CLIENT STATE: {state_log}")
		return self.buy, self.sell

	def get_active_trade(self):
		with open(f"{self.exchange.name}_active_trade{self.suffix}.txt") as json_file:
			data = json.loads(json_file.read())
		return data

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

	def trade_complete(self):
		self.buy_complete = self.exchange.order_complete(self.buy, self.pair) 
		self.sell_complete = self.exchange.order_complete(self.sell, self.pair)
		self.logger.log(f"checking satus: buy: {self.buy_complete} sell: {self.sell_complete}")
		if self.buy_complete and self.sell_complete:
			self.final_sell_bal, self.final_buy_bal = self.get_balances()
			self.calc_metrics()
			state_log = json.dumps({
				"exchange":self.exchange.name,
				"pair":self.pair,
				"threshhold":self.threshhold,
				"trade_amount":self.trade_amount,
				"sell_cur":self.sell_cur,
				"buy_cur":self.buy_cur,
				"sell_complete":self.sell_complete,
				"buy_complete":self.buy_complete,
				"buy_amount":self.buy_amount,
				"sell_amount":self.sell_amount,
				"init_buy_bal":self.init_buy_bal,
				"init_sell_bal":self.init_sell_bal,
				"final_sell_bal":self.final_sell_bal,
				"final_buy_bal":self.final_buy_bal,
				"init_bal_normalized":self.init_bal_normalized,
				"final_bal_normalized":self.final_bal_normalized,
				"margin":self.margin,
				"gain":self.gain,
				"id":self.id
			})
			self.logger.log(f"PAIR CLIENT STATE: {state_log}")
			return True
		return False

	def only_one_trade_complete(self):
		self.buy_complete = self.exchange.order_complete(self.buy, self.pair) 
		self.sell_complete = self.exchange.order_complete(self.sell, self.pair)
		self.logger.log(f"checking single order satus: buy: {self.buy_complete} sell: {self.sell_complete}")
		if (self.buy_complete and not self.sell_complete) or (self.sell_complete and not self.buy_complete):
			return True
		return False

	def cancel_open_trade(self):
		self.buy_complete = self.exchange.order_complete(self.buy, self.pair) 
		self.sell_complete = self.exchange.order_complete(self.sell, self.pair)
		order_to_cancel=None
		if self.buy_complete and not self.sell_complete:
			order_to_cancel = self.buy
		elif self.sell_complete and not self.buy_complete:
			order_to_cancel = self.sell
		else:
			self.logger.log(f"not cancelling open orders: buy complete: {self.buy_complete} sell complete: {self.sell_complete}")
			return False
		self.logger.log(f"cancelling open orders: buy complete: {self.buy_complete} sell complete: {self.sell_complete} order to cancel: {order_to_cancel}")
		return self.exchange.cancel(self.pair, order_to_cancel)

	def calc_metrics(self):
		self.init_bal_normalized = self.init_buy_bal + self.init_sell_bal * self.sell_price
		self.final_bal_normalized = self.final_buy_bal + self.final_sell_bal * self.sell_price
		self.margin = self.final_bal_normalized - self.init_bal_normalized
		self.gain = 100 * self.margin / self.init_bal_normalized

