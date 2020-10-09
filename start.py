from strategy.steps.pair_and_stop_strategy import PairAndStopStrategy
from configs.pair_and_stop_config import get_config
from os import environ
import traceback
from time import sleep

import sys

config = get_config()
bot = PairAndStopStrategy(config)
## Check for state file and if one exists, run regen instead
sys.exit()
bot.initialize()
while True:
	bot.run_interval()
	time.sleep(100)