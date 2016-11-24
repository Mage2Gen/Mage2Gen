import unittest
import os

from mage2gen import Module
from mage2gen.snippets import ApiSnippet
from tests import utils


class TestSnippetApi(unittest.TestCase):

	def test_snippet(self):
		module = Module(package='Package', name='Name', description='Description')
		snippet = ApiSnippet(module)
		sample_output = snippet.add(api_name='SampleAPI', api_method='GET')

		result = utils.CodeSniffer.generate_and_test(module)
		self.assertTrue(result)

	def tearDown(self):
		utils.CodeSniffer.cleanup()
