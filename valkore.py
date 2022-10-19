import os
import sys
import init

from threading import Thread
from subprocess import PIPE, Popen
from queue import Queue, Empty
from sched import scheduler
from time import time, sleep

try:
	# check if we can import main modules
	from modules.logger.logger import Logger
	from modules.config.config import Config

except ImportError:
	# if not, initialize download
	if init.init():
		from modules.logger.logger import Logger
		from modules.config.config import Config
	else:
		# error
		exit(1)


LOGGER = Logger(path="modules/logger/config.ini", name="valkore")
CONFIG = Config(path="config.ini").readConfig()


class ValKore:

	def __init__(self):
		self._timer = scheduler(time, sleep)
		self._timerInterval = int(CONFIG['Settings']['interval'])  # config [sec]
		self._timerPrio = 1
		self.modules = self.getModules()


	def getModules(self) -> dict:
		"""Go through 'modules' directory.

		- Loads if config and py exist

		:return: Modules Configuration
		"""
		modules = next(os.walk('modules'))[1]
		load = {}

		for module in modules:
			files = next(os.walk(f"modules/{module}"))[2]
			if "config.ini" in files and f"{module}.py" in files:
				modCfg = Config(path=f"modules/{module}/config.ini").readConfig()
				appName = modCfg['VKore']['name']
				appVersion = modCfg['VKore']['version']
				appAuthor = f"Author: {modCfg['VKore']['author']}"
				appEditor = f"{appAuthor} | Editor: {modCfg['VKore']['modify']}" if "modify" in modCfg['VKore'] else appAuthor
				LOGGER.Info(f"Loading module: {appName} | v{appVersion} | {appEditor}")
				load[module] = modCfg
			else:
				LOGGER.Warn(f"Loading error: {module}")

		return load


	def startModule(self, modlue: str, cfg: dict):
		"""Start a Valkore Module in an own thread.

		:param modlue: Module to start
		:param cfg: Configuration
		"""

		ON_POSIX = 'posix' in sys.builtin_module_names
		server_thread = f"{modlue}"

		# put output in queue
		def enqueue_output(out, queue):
			for line in iter(out.readline, b''):
				queue.put(line)
			out.close()

		cwd = f"modules\\{modlue}"
		cmd = Popen(["python", f"{modlue}.py"], cwd=cwd, stdout=PIPE, close_fds=ON_POSIX)
		que = Queue()
		trd = Thread(target=enqueue_output, name=server_thread, args=(cmd.stdout, que))
		trd.daemon = True  # thread dies with the program
		trd.start()

		# read line without blocking
		try:
			line = que.get_nowait()
		except Empty:
			pass
		else:  # got line
			LOGGER.Debug(f"{modlue} Output: {line}")


	def startModuleInterval(self, schedule):
		"""Start a Valkore Module in a given interval.

		:param schedule: Sched scheduler
		"""
		for module, cfg in self.modules.items():
			if cfg['VKore']['interval'] == "True" or cfg['VKore']['interval'] == "true":
				self.startModule(module, cfg)
		self._timer.enter(self._timerInterval, self._timerPrio, self.startModuleInterval, (schedule,))


	# Startup
	def run(self):
		"""Starts the Valkore application.

		- Go through all modules
		- Install dependencies if needed
		- Check if start as interval
		- Check if start immediate
		"""
		LOGGER.Info(f"*" * 77)

		# go through all modules
		if len(self.modules) > 0:
			start = False
			for module, cfg in self.modules.items():

				# install dependencies
				if 'Dependency' in cfg:
					init.getDependency(cfg, LOGGER)

				# check if interval..
				if cfg['VKore']['interval'] == "True" or cfg['VKore']['interval'] == "true":
					LOGGER.Info(f"Scheduler: {cfg['VKore']['name']}")
					start = True
				# ..or if autostart
				elif cfg['VKore']['autostart'] == "True" or cfg['VKore']['autostart'] == "true":
					LOGGER.Info(f"Autostart: {cfg['VKore']['name']}")
					self.startModule(module, cfg)
					start = True

			# nothing to start and /or only libraries
			if start is False:
				LOGGER.Info(f"No modules started or scheduled")

		# this should never happen, as VKore itself needs two modules
		else:
			LOGGER.Info(f"No modules loaded")
		LOGGER.Info(f"*" * 77)

		# Start and enter Interval Timer
		self._timer.enter(1, self._timerPrio, self.startModuleInterval, (self._timer,))
		self._timer.run()


# start up framework
if __name__ == '__main__':

	# Write log
	LOGGER.Info(f"*" * 77)
	LOGGER.Info(f"PROJECT     : {CONFIG['VKore']['name']} | ..a project by VALKYTEQ")
	LOGGER.Info(f"DESCRIPTION : {CONFIG['VKore']['description']}")
	LOGGER.Info(f"AUTHOR      : {CONFIG['VKore']['author']}")
	LOGGER.Info(f"VERSION     : {CONFIG['VKore']['version']}")
	LOGGER.Info(f"*" * 77)

	vk = ValKore()
	vk.run()
