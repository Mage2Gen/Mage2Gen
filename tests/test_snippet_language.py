import unittest
import os

from mage2gen import Module
from mage2gen.snippets import LanguageSnippet
from tests import utils


class TestSnippetLanguage(unittest.TestCase):

	def test_snippet(self):
		module = Module(package='Package', name='Name', description='Description')
		snippet = LanguageSnippet(module)
		sample_output = snippet.add('nl_NL')

		result = utils.CodeSniffer.generate_and_test(module)
		self.assertTrue(result)

	def tearDown(self):
		utils.CodeSniffer.cleanup()
