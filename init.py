import os
import json
import configparser
from subprocess import check_output
from urllib.request import urlopen


def init() -> bool:
	"""Initialize Valkore on first startup.

	:return: True if install successful
	"""
	# we print as we don't have logger yet
	print(f"*" * 77)
	print("VALKORE - Valkyrie Core")
	print(f"-" * 77)
	print("Initializing Valkore Dependencies")
	print(f"*" * 77)
	input("Press Enter to continue...")

	# we read manually as we don't have config yet
	cfg = configparser.ConfigParser()
	cfg.read("config.ini")

	# try to install dependencies
	if getDependency(cfg):
		return True
	else:
		return False


def getDependency(config: dict, logger=None) -> bool:
	"""Installs all dependencies found in the module's configuration.

	:param config: Module Configuration
	:param logger: Can be None for initialization
	:return: True if all dependencies are installed
	"""
	step = 0
	lookup = urlopen("https://valky.dev/api/valkore/")
	whitelist = json.loads(lookup.read())

	for mod, ver in config['Dependency'].items():

		if mod in whitelist:
			if not os.path.isdir(f"modules/{mod}"):
				out = check_output(f"git clone {whitelist[mod]} modules/{mod}")
				if not out:
					step = step + 1
					if logger:
						logger.Info(f"Step {step}: '{mod}' download complete")
					else:
						print(f"Step {step}: '{mod}' download complete")
				if not os.path.isdir(f"modules/{mod}"):
					if logger:
						logger.Error(f"Step {step}: Error downloading '{mod}'!")
					else:
						print(f"Step {step}: Error downloading '{mod}'!")
					return False

		else:
			if logger:
				logger.Error(f"Step {step}: '{mod}' not whitelisted!")
			else:
				print(f"Step {step}: '{mod}' not whitelisted!")
			return False

	return True
