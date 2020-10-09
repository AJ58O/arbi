import statistics
from util.logger import logger
import uuid
import json

class StopClient:
	def __init__(self, exchange, pair, threshhold, trade_amount, starting_price=None, run_trade=False, regen=False, log_suffix="", trade_id=None):
		self.exchange = exchange
		self.suffix = log_suffix
		self.pair = pair
		self.threshhold = threshhold
		self.trade_amount = trade_amount
		self.sell_cur = self.pair.split("-")[0]
		self.buy_cur = self.pair.split("-")[1]
		self.cur_trade_price = None
		self.cur_avg_price = None
		self.trade = None
		self.active_trade_type = None
		self.starting_price = starting_price if starting_price != None else statistics.mean([self.exchange.get_buy_price(self.pair),self.exchange.get_sell_price(self.pair)])
		self.trade_active = False
		self.id = trade_id if trade_id is not None else str(uuid.uuid1())
		self.logger = logger(f"STATE_stop_trade_{self.id}", f"LOGS_stop_trade_{self.id}", f"LOGS_stop_trade_{self.id}")
		self.logger.log(f"trade initialized: {self.id}")
		state_log = json.dumps({
			"exchange":self.exchange.name,
			"pair":self.pair,
			"threshhold":self.threshhold,
			"trade_amount":self.trade_amount,
			"sell_cur":self.sell_cur,
			"buy_cur":self.buy_cur,
			"cur_trade_price":self.cur_trade_price,
			"cur_avg_price":self.cur_avg_price,
			"trade":self.trade,
			"active_trade_type":self.active_trade_type,
			"starting_price":self.starting_price,
			"trade_active":self.trade_active,
			"id":self.id
		})

		self.logger.log(f"STOP CLIENT STATE: {state_log}")

	def should_move(self, price1, price2, threshhold, method):
		should_move = False
		if method == "sell":
			cur_spread = abs(float(price1) - float(price2)) / min(float(price1), float(price2))
		elif method == "buy":
			cur_spread = abs(float(price1) - float(price2)) / max(float(price1), float(price2))
		
		should_move = cur_spread > float(threshhold)
		
		message = json.dumps({
			"price1":price1,
			"price2":price2,
			"threshhold":threshhold,
			"method":method,
			"should_move":should_move,
			"cur_spread":cur_spread,
		})
		self.logger.log(f"should move eval: {message}")
		return should_move

	def get_new_limit_price(self, price, threshhold, method):
		if method.lower() == "buy":
			return float(price) + float(price) * float(threshhold)
		elif method == "sell":
			return float(price) - float(price) * float(threshhold)
		return False

	def stop_buy(self, market, amount, price, stop_limit):
		return self.exchange.stop_buy(market, amount, price, stop_limit)

	def stop_sell(self, market, amount, price, stop_limit):
		return self.exchange.stop_sell(market, amount, price, stop_limit)

	def move_order(self, market, amount, price, stop_limit, method, order_id=None):
		if order_id is not None:
			self.exchange.cancel(market, order_id)
		if method.lower() == "sell":
			return self.stop_sell(market, amount, price, stop_limit)
		elif method.lower() == "buy":
			return self.stop_buy(market, amount, price, stop_limit)
		return False

	def eval_and_move(self, market, amount, price, method, current_price, threshhold, order_id=None):
		if self.should_move(price, current_price, threshhold, method) == True:
			new_price = self.get_new_limit_price(current_price, threshhold)
			return self.move_order(market, amount, new_price, new_price, order_id, method)
		return False


	def do_trade(self):
		self.cur_avg_price = statistics.mean([self.exchange.get_buy_price(self.pair),self.exchange.get_sell_price(self.pair)])
		if self.trade_active == False:
			if self.should_move(self.cur_avg_price, self.starting_price, self.threshhold, "sell"):
				self.trade_active = True
				self.active_trade_type = "sell"
				self.cur_trade_price = self.cur_avg_price
				self.trade = self.stop_sell(self.pair, self.trade_amount, self.cur_avg_price, self.get_new_limit_price(self.cur_avg_price, self.threshhold, self.active_trade_type))
				state_log = json.dumps({
					"exchange":self.exchange.name,
					"pair":self.pair,
					"threshhold":self.threshhold,
					"trade_amount":self.trade_amount,
					"sell_cur":self.sell_cur,
					"buy_cur":self.buy_cur,
					"cur_trade_price":self.cur_trade_price,
					"cur_avg_price":self.cur_avg_price,
					"trade":self.trade,
					"active_trade_type":self.active_trade_type,
					"starting_price":self.starting_price,
					"trade_active":self.trade_active,
					"id":self.id
				})
				self.logger.log(f"STOP CLIENT STATE: {state_log}")
				return self.trade
			elif self.should_move(self.cur_avg_price, self.starting_price, self.threshhold, "buy"):
				self.trade_active = True
				self.active_trade_type = "buy"
				self.cur_trade_price = self.cur_avg_price
				self.trade = self.stop_buy(self.pair, self.trade_amount, self.cur_avg_price, self.get_new_limit_price(self.cur_avg_price, self.threshhold, self.active_trade_type))
				state_log = json.dumps({
					"exchange":self.exchange.name,
					"pair":self.pair,
					"threshhold":self.threshhold,
					"trade_amount":self.trade_amount,
					"sell_cur":self.sell_cur,
					"buy_cur":self.buy_cur,
					"cur_trade_price":self.cur_trade_price,
					"cur_avg_price":self.cur_avg_price,
					"trade":self.trade,
					"active_trade_type":self.active_trade_type,
					"starting_price":self.starting_price,
					"trade_active":self.trade_active,
					"id":self.id
				})
				self.logger.log(f"STOP CLIENT STATE: {state_log}")
				return self.trade
		else:
			cur_trade = self.eval_and_move(self.pair, self.trade_amount, self.cur_trade_price, self.active_trade_type, self.cur_avg_price, self.threshhold, self.trade)
			if cur_trade:
				self.trade = cur_trade
				self.cur_trade_price = self.cur_avg_price
				state_log = json.dumps({
					"exchange":self.exchange.name,
					"pair":self.pair,
					"threshhold":self.threshhold,
					"trade_amount":self.trade_amount,
					"sell_cur":self.sell_cur,
					"buy_cur":self.buy_cur,
					"cur_trade_price":self.cur_trade_price,
					"cur_avg_price":self.cur_avg_price,
					"trade":self.trade,
					"active_trade_type":self.active_trade_type,
					"starting_price":self.starting_price,
					"trade_active":self.trade_active,
					"id":self.id
				})
				self.logger.log(f"STOP CLIENT STATE: {state_log}")
				return self.trade
		state_log = json.dumps({
			"exchange":self.exchange.name,
			"pair":self.pair,
			"threshhold":self.threshhold,
			"trade_amount":self.trade_amount,
			"sell_cur":self.sell_cur,
			"buy_cur":self.buy_cur,
			"cur_trade_price":self.cur_trade_price,
			"cur_avg_price":self.cur_avg_price,
			"trade":self.trade,
			"active_trade_type":self.active_trade_type,
			"starting_price":self.starting_price,
			"trade_active":self.trade_active,
			"id":self.id
		})
		self.logger.log(f"STOP CLIENT STATE: {state_log}")
		return False

	def trade_complete(self):
		self.logger.log(f"checking completion status: {self.trade} {self.pair}")
		if self.exchange.order_complete(self.trade, self.pair):
			return True
		return False
