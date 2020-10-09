import json
import datetime

class logger:
	def __init__(self, state_filename, stderr, stdout):
		self.state_filename = state_filename
		self.stderr = stderr
		self.stdout = stdout

	def log_state(self, obj):
		try:
			with open(self.state_filename, 'w') as outfile:
				json.dump(obj.__dict__, outfile)
		except:
			with open(self.state_filename, 'w') as outfile:
				json.dump(obj, outfile)

	def log(self, message, error=False):
		filename = self.stdout if not error else self.stderr
		log_type = "[info]" if not error else "[error]"
		log_output = f"{datetime.datetime.now().isoformat()} - {log_type}: {message}\n"

		with open(filename, 'a') as outfile:
			json.dump(log_output, outfile)


	def regenerate_state(self, obj):
		with open(self.state_filename) as json_file:
			inObj = json.load(json_file)
			for key in inObj.keys():
				setattr(obj, key, inObj[key])