# A Magento 2 module generator library
# Copyright (C) 2016 Derrick Heesbeen
# Copyright (C) 2016 Maikel Martens Changed add API and refactor code
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
import os
from mage2gen import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam

class PluginSnippet(Snippet):

	description = """Creates a Plugin

	Plugins are designed to overwrite core Magento methods or methods from other 3rd party modules. 

	You can choose to change it before, after, or around the original method is called. 

	Example
	-------

	Change the product name to show pipes before and after the name. 

	Input for the plugin form 

	- **classname:** Magento\Catalog\Model\Product 
	- **methodname:** getName
	- **plugintype:** After

	.. code::
		
		public function afterGetName(
			Magento\Catalog\Model\Product $subject,
			$result
		){
			return '|'.$result.'|';
		}

	"""

	TYPE_BEFORE = 'before'
	TYPE_AFTER = 'after'
	TYPE_AROUND = 'around'

	SCOPE_CHOISES = [
		(TYPE_BEFORE, 'Before'),
		(TYPE_AFTER, 'After'),
		(TYPE_AROUND, 'Around'),
	]

	def add(self, classname, methodname, plugintype=TYPE_AFTER, sortorder=10, disabled=False):
		# Add class
		plugin = Phpclass('Plugin\\{}'.format(classname))
		
		variable = '$result'
		if plugintype == self.TYPE_BEFORE:
			variable = '//$functionvariables'
		elif plugintype == self.TYPE_AROUND:
			variable = '\Closure $proceed' 

		plugin.add_method(Phpmethod(
			plugintype + methodname[0].capitalize() + methodname[1:],
			params=[
				'\\' + classname + ' $subject',
				variable
			]
		))
	
		# Add plug first will add the module namespace to PhpClass
		self.add_class(plugin)	

		# Plugin XML
		config = Xmlnode('config', attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:framework:ObjectManager/etc/config.xsd"}, nodes=[
			Xmlnode('type', attributes={'name': classname}, nodes=[
				Xmlnode('plugin', attributes={
					'name': plugin.class_namespace.replace('\\', '_'),
					'type':plugin.class_namespace,
					'sortOrder':sortorder,
					'disabled':'true' if disabled else 'false'
				})
			])
		])

		self.add_xml('etc/di.xml', config)

	@classmethod
	def params(cls):
		return [
			SnippetParam(name='classname', required=True,
				description='This must be the full class path, example: Magento\Catalog\Model\Product',
				regex_validator=r'^[\w\\]+$',
				error_message='Only alphanumeric, underscore and backslash characters are allowed'),
			SnippetParam(name='methodname', required=True,
				regex_validator= r'^\w+$',
				error_message='Only alphanumeric and underscore characters are allowed'),
			SnippetParam(name='plugintype', choises=cls.SCOPE_CHOISES, default=cls.TYPE_AFTER),
			SnippetParam(name='sortorder', default=10, 
				regex_validator=r'^\d*$', 
				error_message='Must be numeric'),
			SnippetParam(name='disabled', yes_no=True),
		]
		
