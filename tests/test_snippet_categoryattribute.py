import unittest
import os

from mage2gen import Module
from mage2gen.snippets import CategoryAttributeSnippet
from tests import utils


class TestSnippetCategoryAttribute(unittest.TestCase):

	def test_snippet(self):
		module = Module(package='Package', name='Name', description='Description')
		snippet = CategoryAttributeSnippet(module)
		sample_output = snippet.add(
			attribute_label='test', 
			frontend_input='select', 
			scope=1, 
			required=False, 
			source_model='custom', 
			source_model_options='value1, value2, value3')

		result = utils.CodeSniffer.generate_and_test(module)
		self.assertTrue(result)

	def tearDown(self):
		utils.CodeSniffer.cleanup()
