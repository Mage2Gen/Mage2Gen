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
from .. import Phpclass, Phpmethod, Xmlnode, Snippet, SnippetParam


class PreferenceSnippet(Snippet):
	snippet_label = 'Preference / Rewrite'

	description = """Create the old school Magento 1 Rewrite, but it is not recommended."""

	def add(self, classname, extra_params=None):
		# Add class
		preference_classname = 'Rewrite\\{}'.format(classname)
		preference_class = Phpclass(preference_classname, "\\{}".format(classname))
		
		# Add plug first will add the module namespace to PhpClass
		self.add_class(preference_class)

		# Plugin XML
		config = Xmlnode('config', attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:framework:ObjectManager/etc/config.xsd"}, nodes=[
			Xmlnode('preference', attributes={
				'for': classname,
				'type': preference_class.class_namespace
			})
		])

		self.add_xml('etc/di.xml', config)

		split_classname = classname.split('\\')
		if len(split_classname) > 1:
			etc_module = Xmlnode('config', attributes={
				'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Module/etc/module.xsd"}, nodes=[
				Xmlnode('module', attributes={'name': self.module_name}, nodes=[
					Xmlnode('sequence', attributes={}, nodes=[
						Xmlnode('module', attributes={'name': '{}_{}'.format(split_classname[0], split_classname[1])})
					])
				])
			])
			self.add_xml('etc/module.xml', etc_module)


	@classmethod
	def params(cls):
		return [
			SnippetParam(name='classname', required=True,
				description='Example: Magento\Sales\Model\Order',
				regex_validator=r'^[\w\\]+$',
				error_message='Only alphanumeric, underscore and backslash characters are allowed'),
		]
		
