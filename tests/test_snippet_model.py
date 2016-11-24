import unittest
import os

from mage2gen import Module
from mage2gen.snippets import ModelSnippet
from tests import utils


class TestSnippetModel(unittest.TestCase):

	def test_snippet(self):
		module = Module(package='Package', name='Name', description='Description')
		snippet = ModelSnippet(module)
		sample_output = snippet.add(
			model_name='test', 
			field_name='name', 
			field_type='text', 
			adminhtml_grid=True, 
			adminhtml_form=True,
			web_api=True)

		result = utils.CodeSniffer.generate_and_test(module)
		self.assertTrue(result)

	def tearDown(self):
		utils.CodeSniffer.cleanup()
