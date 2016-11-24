import unittest
import os

from mage2gen import Module
from mage2gen.snippets import ProductAttributeSnippet
from tests import utils


class TestSnippetProductAttribute(unittest.TestCase):

	def test_snippet(self):
		module = Module(package='Package', name='Name', description='Description')
		snippet = ProductAttributeSnippet(module)
		sample_output = snippet.add('test')

		result = utils.CodeSniffer.generate_and_test(module)
		self.assertTrue(result)

	def tearDown(self):
		utils.CodeSniffer.cleanup()
