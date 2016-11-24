import unittest
import os

from mage2gen import Module
from mage2gen.snippets import CustomerAttributeSnippet
from tests import utils


class TestSnippetCustomerAttribute(unittest.TestCase):

	def test_snippet(self):
		module = Module(package='Package', name='Name', description='Description')
		snippet = CustomerAttributeSnippet(module)
		sample_output = snippet.add(
			attribute_label='test', 
			customer_forms=False, 
			customer_address_forms=False, 
			customer_entity='customer', 
			frontend_input='text',
			static_field_type='varchar', 
			required=False, 
			source_model='custom', 
			source_model_options='value1, value2, value3')

		result = utils.CodeSniffer.generate_and_test(module)
		self.assertTrue(result)

	def tearDown(self):
		utils.CodeSniffer.cleanup()
