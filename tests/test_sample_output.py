import unittest
import os

from mage2gen import Module
from mage2gen.snippets import ApiSnippet
from tests import utils


class TestSampleOutput(unittest.TestCase):

	def test_simple_api(self):
		module = Module(package='Package', name='Name', description='Description')
		snippet = ApiSnippet(module)
		sample_output = snippet.add(api_name='SampleAPI', api_method='GET')

		exitcode = utils.CodeSniffer.generate_and_test(module)
		print(exitcode)

	def tearDown(self):
		utils.CodeSniffer.cleanup()
