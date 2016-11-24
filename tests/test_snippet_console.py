import unittest
import os

from mage2gen import Module
from mage2gen.snippets import ConsoleSnippet
from tests import utils


class TestSnippetconsole(unittest.TestCase):

	def test_snippet(self):
		module = Module(package='Package', name='Name', description='Description')
		snippet = ConsoleSnippet(module)
		sample_output = snippet.add('test', 'test console')

		result = utils.CodeSniffer.generate_and_test(module)
		self.assertTrue(result)

	def tearDown(self):
		utils.CodeSniffer.cleanup()
