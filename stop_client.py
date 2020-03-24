class StopClient:
	def __init__(self, exchange, pair, threshhold, trade_amount, starting_price=None, run_trade=False, regen=False, log_suffix=""):
		self.exchange = exchange
		self.suffix = log_suffix
		self.pair = pair
		self.threshhold = threshhold
		self.trade_amount = trade_amount
		self.sell_cur = self.pair.split("-")[0]
		self.buy_cur = self.pair.split("-")[1]
		self.starting_price = starting_price if starting_price != None else mean([self.exchange.get_buy_price(self.pair),self.exchange.get_sell_price(self.pair)])

	def should_move(self, price1, price2, threshhold, method):
		if method == "sell":
			return abs(float(price1) - float(price2)) / min(float(price1), float(price2)) > float(threshhold)
		elif method == "buy":
			return abs(float(price1) - float(price2)) / max(float(price1), float(price2)) > float(threshhold)
		return False

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
		if order_id != None:
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


	def init_trade(self):
		avg_price = mean([self.exchange.get_buy_price(self.pair),self.exchange.get_sell_price(self.pair)])
		if  self.should_move(avg_price, self.starting_price, self.threshhold, "sell"):
			return "sell"
		elif self.should_move(avg_price, self.starting_price, self.threshhold, "buy"):
			return "buy"
		return False