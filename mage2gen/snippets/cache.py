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
import os
from mage2gen import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam

class CacheSnippet(Snippet):
	description = """
	Custom Cache snippet
	"""

	def add(self, name='', description='', extra_params=None):
		if not name:
			name = self._module.name
		cache_id = '{}_cache_tag'.format(name.lower())
		
		# Add cache class
		cache_class = Phpclass('Model\\Cache\\{}'.format(name), extends='\\Magento\\Framework\\Cache\\Frontend\\Decorator\\TagScope', attributes=[
			"const TYPE_IDENTIFIER = '{}';".format(cache_id),
			"const CACHE_TAG = '{}';".format(cache_id.upper())
		])

		cache_class.add_method(Phpmethod(
			'__construct',
			params=['\Magento\Framework\App\Cache\Type\FrontendPool $cacheFrontendPool'],
			body="parent::__construct($cacheFrontendPool->get(self::TYPE_IDENTIFIER), self::CACHE_TAG);",
			docstring=['@param \\Magento\\Framework\\App\\Cache\\Type\\FrontendPool $cacheFrontendPool']
		))
	
		self.add_class(cache_class)	

		# Cache XML
		cache_xml = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:framework:Cache/etc/cache.xsd"}, nodes=[
			Xmlnode('type', attributes={
				'name': cache_id, 
				'translate': 'label,description',
				'instance': cache_class.class_namespace
				}, nodes=[
				Xmlnode('label', node_text=name),
				Xmlnode('description', node_text=description)
			])
		])

		self.add_xml('etc/cache.xml', cache_xml)

	@classmethod
	def params(cls):
		return [
			SnippetParam(
				name='name',
				description='When empty uses module name',
				required=False,
				regex_validator= r'^[a-zA-Z]{1}\w+$',
				error_message='Only alphanumeric and underscore characters are allowed, and need to start with a alphabetic character.'),
			SnippetParam(
				name='description',
				description='Short description about the cache',
				required=False
			)
		]
		
