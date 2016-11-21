import json
import os
import random
import string
import shutil
from glob import glob

from subprocess import Popen, PIPE

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
PHPCS_PATH = os.path.join(os.path.dirname(BASE_PATH), 'phpcs.phar')


def tmp_path():
	return 'tmp_{}'.format(
		''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
	)


class CodeSniffer:
	class CodeStyleException(Exception):
		def __init__(self, message):
			self.message = message

	@staticmethod
	def cleanup():
		for path in glob(os.path.join(BASE_PATH, 'tmp_*')):
			shutil.rmtree(path)

	@staticmethod
	def generate_and_test(module, *args):
		path = os.path.join(BASE_PATH, tmp_path())

		os.mkdir(path)
		module.generate_module(path)

		results = CodeSniffer(path).test(path, *args)
		CodeSniffer.cleanup()

		return results

	def __init__(self, path):
		self.path = path

	@staticmethod
	def execute(*args):
		command = ['php', PHPCS_PATH]
		for arg in args:
			command.append(arg)

		process = Popen(command, stdin=PIPE, stdout=PIPE)
		return process.communicate()

	@staticmethod
	def test(*args):
		json_encoded, errors = CodeSniffer.execute('--report=json', *args)

		# Parse JSON
		output = json.loads(json_encoded.decode())

		totals = None
		for key, value in output.items():
			if key == 'totals':
				totals = value

		if totals and totals['errors'] > 0:
			nice_format, _ = CodeSniffer.execute('--report=full', *args)
			raise CodeSniffer.CodeStyleException(
				nice_format.decode()
			)

		return True
