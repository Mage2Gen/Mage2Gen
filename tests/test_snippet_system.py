import unittest
import os

from mage2gen import Module
from mage2gen.snippets import SystemSnippet
from tests import utils


class TestSnippetSystem(unittest.TestCase):

	def test_snippet(self):
		module = Module(package='Package', name='Name', description='Description')
		snippet = SystemSnippet(module)
		sample_output = snippet.add(
			tab='test', 
			section='test', 
			group='test', 
			field='test', 
			field_type='select', 
			new_tab=False, 
			source_model='custom', 
			source_model_options='value1, value2, value3')

		result = utils.CodeSniffer.generate_and_test(module)
		self.assertTrue(result)

	def tearDown(self):
		utils.CodeSniffer.cleanup()
