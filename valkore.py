import init

from sched import scheduler
from time import time, sleep

try:
	import tools
	# check if we can import main modules
	from modules.logger.logger import Logger
	from modules.config.config import Config

except ImportError:
	# if not, initialize download
	if init.init():
		import tools
		from modules.logger.logger import Logger
		from modules.config.config import Config
	else:
		# error
		exit(1)


class ValKore:

	def __init__(self, interface=None):
		
		self._timer = scheduler(time, sleep)
		self._timerInterval = int(CONFIG['Settings']['interval'])  # config [sec]
		self._timerPrio = 1

		self.log_ui = None
		if interface is True:
			self.log_ui = valkore_ui.load()
			self.log = Logger(path="modules/logger/config.ini", name="valkore", widget=self.log_ui.getLogWidget())
		else:
			self.log = Logger(path="modules/logger/config.ini", name="valkore", widget=self.log_ui)

		# Write log
		self.log.info(f"-" * 100)
		self.log.info(f"PROJECT     : {CONFIG['VKore']['name']} | ..a project by VALKYTEQ")
		self.log.info(f"DESCRIPTION : {CONFIG['VKore']['description']}")
		self.log.info(f"AUTHOR      : {CONFIG['VKore']['author']}")
		self.log.info(f"VERSION     : {CONFIG['VKore']['version']}")
		self.log.info(f"-" * 100)

		# load modules
		self.modules = tools.loadModules(self.log)

	def startModuleInterval(self, schedule):
		"""Start a Valkore Module in a given interval.

		:param schedule: Sched scheduler
		"""
		for module, cfg in self.modules.items():
			if 'interval' in cfg['VKore']:
				if cfg['VKore']['interval']:
					tools.startModule(self.log, module)
		self._timer.enter(self._timerInterval, self._timerPrio, self.startModuleInterval, (schedule,))

	# Startup
	def run(self):
		"""Starts the Valkore application.

		- Go through all modules
		- Install dependencies if needed
		- Check if start as interval
		- Check if start immediate
		"""
		self.log.info(f"-" * 100)

		# go through all modules
		if len(self.modules) > 0:
			start = False
			for module, cfg in self.modules.items():

				# install dependencies
				if 'Dependency' in cfg:
					init.getDependency(cfg, module, self.log)

				# if not in UI mode:
				if module != "valkore-ui" and self.log_ui is None:
					# check if interval..
					if cfg['VKore']['interval']:
						self.log.info(f"Scheduler: {cfg['VKore']['name']}")
						start = True
					# ..or if autostart
					elif cfg['VKore']['autostart']:
						self.log.info(f"Autostart: {cfg['VKore']['name']}")
						tools.startModule(self.log, module)
						start = True

			# only starting UI
			if self.log_ui is not None:
				self.log.info(f"Autostart: Valkore UI")
			# nothing to start
			if start is False and self.log_ui is None:
				self.log.info(f"No modules started or scheduled")

		# this should never happen, as VKore itself needs three modules
		else:
			self.log.info(f"No modules loaded")
		self.log.info(f"-" * 100)

		# Enter UI loop
		if self.log_ui is not None:
			self.log_ui.mainloop()
		# Start Core loop
		else:
			self._timer.enter(1, self._timerPrio, self.startModuleInterval, (self._timer,))
			self._timer.run()


# start up framework
if __name__ == '__main__':
	CONFIG = Config(path="config.ini").readConfig()
	if CONFIG['Settings']['interface']:
		import importlib
		valkore_ui = importlib.import_module("modules.valkore-ui.valkore-ui")
		isUi = True
	else:
		valkore_ui = None
		isUi = False

	vk = ValKore(isUi)
	vk.run()
