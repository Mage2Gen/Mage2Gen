import os, locale
from mage2gen import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam

class EmptySnippet(Snippet):

	snippet_label = 'Your label'

	description = """

    """

	def add(self):

	@classmethod	
	def params(cls):
		return []

	@classmethod
    def extra_params(cls):
    	return []	
