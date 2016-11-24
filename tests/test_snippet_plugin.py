import unittest
import os

from mage2gen import Module
from mage2gen.snippets import PluginSnippet
from tests import utils


class TestSnippetPlugin(unittest.TestCase):

	def test_snippet(self):
		module = Module(package='Package', name='Name', description='Description')
		snippet = PluginSnippet(module)
		sample_output = snippet.add('Magento\\Catalog\\Model\\Product', 'getName')

		result = utils.CodeSniffer.generate_and_test(module)
		self.assertTrue(result)

	def tearDown(self):
		utils.CodeSniffer.cleanup()
