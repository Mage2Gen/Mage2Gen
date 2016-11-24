import unittest
import os

from mage2gen import Module
from mage2gen.snippets import ObserverSnippet
from tests import utils


class TestSnippetObserver(unittest.TestCase):

	def test_snippet(self):
		module = Module(package='Package', name='Name', description='Description')
		snippet = ObserverSnippet(module)
		sample_output = snippet.add('catalog_product_save_after')

		result = utils.CodeSniffer.generate_and_test(module)
		self.assertTrue(result)

	def tearDown(self):
		utils.CodeSniffer.cleanup()
