import os
import sys

from threading import Thread
from subprocess import PIPE, Popen, check_output
from queue import Queue, Empty
from sched import scheduler
from time import time, sleep

from modules.logger.logger import Logger
from modules.config.config import Config
from modules.database.database import Database


LOGGER = Logger(path="modules/logger/config.ini", name="valkframe")
CONFIG = Config(path="config.ini").readConfig()
DB = Database(LOGGER, CONFIG)


class ValkFrame:

	def __init__(self):
		self._timer = scheduler(time, sleep)
		self._timerInterval = int(CONFIG['Base']['interval'])  # config [sec]
		self._timerPrio = 1


	def getModules(self) -> dict:
		modules = next(os.walk('modules'))[1]
		load = {}

		for module in modules:
			files = next(os.walk(f"modules/{module}"))[2]
			if "config.ini" in files and f"{module}.py" in files:
				modCfg = Config(path=f"modules/{module}/config.ini").readConfig()
				LOGGER.Info(f"Loading module: {modCfg['Base']['name']} (v{modCfg['Base']['version']} | {modCfg['Base']['author']})")
				load[module] = modCfg
			else:
				LOGGER.Warn(f"Missing dependency: {module}")

		return load


	def startModule(self, modlue, cfg):

		ON_POSIX = 'posix' in sys.builtin_module_names
		server_thread = f"{modlue}"

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
			LOGGER.Info(f"Started module: {cfg['Base']['name']}")
		else:  # got line
			LOGGER.Debug(f"{modlue} Output: {line}")


	def controller(self, schedule):
		self._timer.enter(self._timerInterval, self._timerPrio, self.controller, (schedule,))


	# Startup
	def run(self):
		"""
		- Loads CONFIG Version Information
		- Starts CONFIG Observer
		"""
		# Write log
		LOGGER.Info(f"*"*69)
		LOGGER.Info(f"PROJECT     : {CONFIG['Base']['name']} | ..a project by VALKYTEQ")
		LOGGER.Info(f"DESCRIPTION : {CONFIG['Base']['description']}")
		LOGGER.Info(f"AUTHOR      : {CONFIG['Base']['author']}")
		LOGGER.Info(f"VERSION     : {CONFIG['Base']['version']}")
		LOGGER.Info(f"*"*69)

		# load modules
		modules = vf.getModules()
		if len(modules) > 0:
			for module, cfg in modules.items():
				vf.startModule(module, cfg)
		else:
			LOGGER.Info(f"No modules loaded")
		# LOGGER.Info(f"-" * 69)

		# Start and enter Interval Timer
		self._timer.enter(1, self._timerPrio, self.controller, (self._timer,))
		self._timer.run()


# start up framework
if __name__ == '__main__':

	vf = ValkFrame()
	vf.run()
