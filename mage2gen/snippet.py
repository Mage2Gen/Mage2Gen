# A Magento 2 module generator library
# Copyright (C) 2016 Maikel Martens
#
# This file is part of Mage2Gen.
#
# Mage2Gen is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
import inspect
from collections import namedtuple

SnippetParam = namedtuple('SnippetParam', 'name description required default choises yes_no')
SnippetParam.__new__.__defaults__ = ('', False, None, None, None)

class MetaClass(type):
	snippets = []
	
	def __new__(cls, clsname, bases, attrs):
		newclass = super(MetaClass, cls).__new__(cls, clsname, bases, attrs)
		if clsname != 'Snippet':
			MetaClass.snippets.append(newclass)
		return newclass

class Snippet(metaclass=MetaClass):
	snippet_name = None
	description = ''

	def __init__(self, module):
		self._module = module

	@classmethod
	def snippets(cls):
		return type(cls).snippets

	@classmethod
	def name(cls):
		if cls.snippet_name:
			return sel.snippet_name
		return cls.__name__.lower().replace('snippet', '').capitalize()
	
	@classmethod
	def params(cls):
		params = []
		for arg_name, arg in inspect.signature(cls.add).parameters.items():
			if arg_name == 'self':
				continue
			default = arg.default if arg.default != arg.empty else None
			
			params.append(SnippetParam(
				name=arg_name, 
				required=arg.default == arg.empty,
				default=default,
				yes_no=isinstance(default, bool),
				))
		return params


	@property
	def module_name(self):
	    return self._module.module_name

	def add_class(self, phpclass):
		return self._module.add_class(phpclass)

	def add_xml(self, xml_file, node):
		return self._module.add_xml(xml_file, node)

	def add_static_file(self, path, staticfile):
		return self._module.add_static_file(path, staticfile)

	def add(self, *args, **kwargs):
		raise Exception('Not implemented')