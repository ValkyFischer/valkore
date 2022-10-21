import configparser

from tools import getDependency


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
