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
	print(f"-" * 100)
	print("VALKORE - Valkyrie Core")
	print(f"-" * 100)
	print("Initializing Valkore Dependencies")
	print(f"-" * 100)
	input("Press Enter to continue...")

	# we read manually as we don't have config yet
	cfg = configparser.ConfigParser()
	cfg.read("config.ini")

	# try to install dependencies
	if getDependency(cfg, "Valkore"):
		return True
	else:
		return False


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
					logger.Info(f"{module}: Found dependency '{mod}'")
				else:
					print(f"{module}: Found dependency '{mod}'")
				out = check_output(f"git clone {whitelist[mod]} modules/{mod}")
				if not out:
					if logger:
						logger.Info(f"{module}: '{mod}' download complete")
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
