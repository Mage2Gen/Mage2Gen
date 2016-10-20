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
import re
import inspect
from collections import namedtuple

from mage2gen.utils import upperfirst

class SnippetParam:
	"""
	SnippetParam defines how a param can be rendered and validated by external program.

	depend is a dict where the key is the name of an other param and the value is a regex, example:
	{
		'some_param': r'value|value2'
	}
	"""
	
	def __init__(
		self, name, description='', required=False, default=None, 
		choises=None, yes_no=False, regex_validator='', error_message='',
		depend=None, label=None, multiple_choices=False, repeat=False
	):
		self.name = name
		self.description = description
		self.required = required
		self.default = default
		self.choises = choises
		self.yes_no = yes_no
		self.regex_validator = regex_validator
		self.error_message = error_message
		self.depend = depend
		self.label = label if label else upperfirst(name.replace('_', ' '))
		self.multiple_choices = multiple_choices
		self.repeat = repeat

	def name_label(self):
		return upperfirst(self.name.replace('_', ' '))

	def validate(self, value):
		re_validate = re.compile(self.regex_validator)

		if self.required and not value:
			raise Exception('This field is required')

		if self.regex_validator and not re_validate.match(value):
			raise Exception(self.error_message)

class MetaClass(type):
	snippets = []
	
	def __new__(cls, clsname, bases, attrs):
		newclass = super(MetaClass, cls).__new__(cls, clsname, bases, attrs)
		if clsname != 'Snippet':
			MetaClass.snippets.append(newclass)
		return newclass

class Snippet(metaclass=MetaClass):
	snippet_label = None
	description = ''

	def __init__(self, module):
		self._module = module

	@classmethod
	def snippets(cls):
		return type(cls).snippets

	@classmethod
	def label(cls):
		if cls.snippet_label:
			return cls.snippet_label
		return cls.name()

	@classmethod
	def name(cls):
		return cls.__name__.lower().replace('snippet', '').capitalize()
	
	@classmethod
	def params(cls):
		params = []
		for arg_name, arg in inspect.signature(cls.add).parameters.items():
			if arg_name == 'self' or arg_name == 'extra_params':
				continue
			default = arg.default if arg.default != arg.empty else None
			
			params.append(SnippetParam(
				name=arg_name, 
				required=arg.default == arg.empty,
				default=default,
				yes_no=isinstance(default, bool),
				))
		return params

	@classmethod
	def extra_params(cls):
		"""
		Gives a list of optional params, these params must be given to the add functon in a dict for the keyword extra_params.

		To seperate params with a title, add a string with name in the list between the items. 
		"""
		return []


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
