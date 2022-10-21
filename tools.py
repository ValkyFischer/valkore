import os
import sys
from queue import Queue, Empty
from subprocess import Popen, PIPE, check_output
from threading import Thread
from urllib.request import urlopen

from flask import json



def loadModules(logger=None) -> dict:
	"""Go through 'modules' directory.

	- Loads if config and py exist

	:return: Modules Configuration
	"""
	from modules.config.config import Config

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
			if logger is not None:
				logger.info(f"Loading module: {appName} | v{appVersion} | {appEditor}")
			load[module] = modCfg
		else:
			if logger is not None:
				logger.Warn(f"Loading error: {module}")

	return load


def startModule(logger: any, modlue: str):
	"""Start a Valkore Module *.py file in an own thread.

	:param logger: Logger object
	:param modlue: Module to start
	"""

	ON_POSIX = 'posix' in sys.builtin_module_names
	server_thread = f"{modlue}"

	# put output in queue
	def enqueue_output(out, queue):
		for bline in iter(out.readline, b''):
			queue.put(bline)
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
		logger.info(f"{modlue} Output: {line}")


def runModule(logger: any, modlue: str):
	"""Start a Valkore Module by run() in an own thread.

	:param logger: Logger object
	:param modlue: Module name
	:return:
	"""
	import importlib
	dyn_module = importlib.import_module(f"modules.{modlue}.{modlue}")

	trd = Thread(target=dyn_module.run, name=modlue, args=(logger,))
	trd.daemon = True
	trd.start()


def getModule(module: str, logger: any, whitelist: dict):
	logger.info(f"{module}: Starting module download")
	out = check_output(f"git clone {whitelist[module]['link']} modules/{module}")
	if not out:
		if logger:
			logger.info(f"{module}: Module download complete")


def getDependency(config: dict, module: str, logger=None) -> bool:
	"""Installs all dependencies found in the module's configuration.

	:param module: Module Name
	:param config: Module Configuration
	:param logger: Can be None for initialization
	:return: True if all dependencies are installed
	"""
	lookup = urlopen("https://valky.dev/api/valkore/")
	whitelist = json.loads(lookup.read())

	for mod, ver in config['Dependency'].items():

		if mod in whitelist:
			if not os.path.isdir(f"modules/{mod}"):
				if logger:
					logger.info(f"{module}: Found dependency '{mod}'")
				else:
					print(f"{module}: Found dependency '{mod}'")
				out = check_output(f"git clone {whitelist[mod]['link']} modules/{mod}")
				if not out:
					if logger:
						logger.info(f"{module}: '{mod}' download complete")
					else:
						print(f"{module}: '{mod}' download complete")
				if not os.path.isdir(f"modules/{mod}"):
					if logger:
						logger.Error(f"{module}: Error downloading '{mod}'!")
					else:
						print(f"{module}: Error downloading '{mod}'!")
					return False

		else:
			# TODO: pip install
			if logger:
				logger.Error(f"{module}: '{mod}' not whitelisted!")
			else:
				print(f"{module}: '{mod}' not whitelisted!")
			return False

	return True
