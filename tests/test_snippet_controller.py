import unittest
import os

from mage2gen import Module
from mage2gen.snippets import ControllerSnippet
from tests import utils


class TestSnippetController(unittest.TestCase):

	def test_snippet(self):
		module = Module(package='Package', name='Name', description='Description')
		snippet = ControllerSnippet(module)
		sample_output = snippet.add(
			frontname='test', 
			section='index', 
			action='index', 
			adminhtml=False, 
			ajax=False)

		result = utils.CodeSniffer.generate_and_test(module)
		self.assertTrue(result)

	def test_snippet_admin(self):
		module = Module(package='Package', name='Name', description='Description')
		snippet = ControllerSnippet(module)
		sample_output = snippet.add(
			frontname='test', 
			section='index', 
			action='index', 
			adminhtml=True, 
			ajax=False)

		result = utils.CodeSniffer.generate_and_test(module)
		self.assertTrue(result)

	def test_snippet_ajax(self):
		module = Module(package='Package', name='Name', description='Description')
		snippet = ControllerSnippet(module)
		sample_output = snippet.add(
			frontname='test', 
			section='index', 
			action='index', 
			adminhtml=False, 
			ajax=True)

		result = utils.CodeSniffer.generate_and_test(module)
		self.assertTrue(result)

	def tearDown(self):
		utils.CodeSniffer.cleanup()
