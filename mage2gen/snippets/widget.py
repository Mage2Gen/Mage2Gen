# A Magento 2 module generator library
# Copyright (C) 2016 Derrick Heesbeen
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
from mage2gen.utils import upperfirst


class WidgetSnippet(Snippet):
	description = """
	
	"""

	TYPE_CHOISES = [
		('text', 'Text'),
		('select', 'Select'),
		('multiselect', 'Multiselect'),
	]
	
	def add(self, name, field, field_type='text', sortorder=10, extra_params=None):

		widget_block = Phpclass(
			'\\'.join(['Block','Widget',name]),
			implements=['BlockInterface'],
			dependencies=['Magento\Framework\View\Element\Template','Magento\Widget\Block\BlockInterface'],
			extends='Template',
			attributes=['protected $_template = "widget/{}.phtml";'.format(name.lower())]
		)

		self.add_class(widget_block)

		parameter_attributes = {'name': field.lower(),'xsi:type': field_type,'visible': 'true','sort_order': sortorder}

		if field_type == 'select' or field_type == 'multiselect':
			parameter_attributes["source_model"] = "Magento\\Config\\Model\\Config\\Source\\Yesno"

		widget_file = 'etc/widget.xml'

		widget_xml = Xmlnode('widgets',attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Widget:etc/widget.xsd"},nodes=[
			Xmlnode('widget',attributes={'id':'{}_{}_{}'.format(self._module.package.lower(),self._module.name.lower(),name.lower()),'class':widget_block.class_namespace},nodes=[
				Xmlnode('label',node_text=name),
				Xmlnode('description',node_text=name),
				Xmlnode('parameters',nodes=[
					Xmlnode('parameter',
					attributes=parameter_attributes, 
					nodes=[
						Xmlnode('label',node_text=field)
					])
				])	
			])
		]);

		self.add_xml(widget_file, widget_xml)

		path = os.path.join('view','frontend','templates')
		self.add_static_file(path, StaticFile("{}/{}.phtml".format('widget', name),body="<?php if($block->getData('{name}')): ?>\n\t<h2 class='{name}'><?php echo $block->getData('{name}'); ?></h2>\n<?php endif; ?>".format(name=field.lower(),classname=widget_block.class_namespace)))

	@classmethod
	def params(cls):
		return [
			SnippetParam(
				name='name',
				description='Example: productStock',
				required=True,
				regex_validator= r'^[a-zA-Z]{1}\w+$',
				error_message='Only alphanumeric and underscore characters are allowed, and need to start with a alphabetic character.',
				repeat=True),
			SnippetParam(
				name='field', 
				required=True, 
				description='Example: product_id',
				regex_validator= r'^[a-zA-Z]{1}\w+$',
				error_message='Only alphanumeric and underscore characters are allowed, and need to start with a alphabetic character.'),
			SnippetParam(
				name='field_type', 
				choises=cls.TYPE_CHOISES, 
				default='text'),
			SnippetParam(name='sortorder', default=10, 
				regex_validator=r'^\d*$', 
				error_message='Must be numeric')
		]

	@classmethod
	def extra_params(cls):
		return [

		]	