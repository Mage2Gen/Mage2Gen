# A Magento 2 module generator library
# Copyright (C) 2017 Mr. Lewis
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
from .. import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam

class BlockSnippet(Snippet):

	description = """Creates just a Block

	Create a Simple Block for the Frontend or Adminhtml. 
	It is also possible to insert the block based on a layout handle and a reference.

	Example
	-------

	Create a Notice Block

	Input for the block form 

	- **classname:** Notices
	- **methodname:** getCustomNotice
	- **scope:** Frontend
	- **layout handle:** default
	- **reference type:** Container
	- **reference name:** content

	"""

	SCOPE_FRONTEND = 'frontend'
	SCOPE_ADMINHTML = 'backend'

	SCOPE_CHOISES = [
		(SCOPE_FRONTEND, 'Frontend'),
		(SCOPE_ADMINHTML, 'Backend'),
	]

	REFERENCE_CONTAINER = 'referenceContainer'
	REFERENCE_BLOCK = 'referenceBlock'

	REFERENCE_CHOISES = [
		(REFERENCE_CONTAINER, 'Container'),
		(REFERENCE_BLOCK, 'Block'),
	]

	def add(self, classname, methodname, scope=SCOPE_FRONTEND, layout_handle=None, reference_type=REFERENCE_CONTAINER, reference_name='content', extra_params=None):
		# Add class
		block = Phpclass('Block\\{}'.format(classname),'\Magento\Framework\View\Element\Template')
		scope_name = 'frontend'
		context_class = '\Magento\Framework\View\Element\Template\Context'
		if scope == self.SCOPE_ADMINHTML:
			block = Phpclass('Block\\Adminhtml\\{}'.format(classname), '\Magento\Backend\Block\Template')
			scope_name = 'adminhtml'
			context_class = '\Magento\Backend\Block\Template\Context'

		block.add_method(Phpmethod(
				'__construct',
				params=[
					context_class + ' $context',
					'array $data = []',
				],
				body="""parent::__construct($context, $data);""",
				docstring=[
					'Constructor',
					'',
					'@param ' + context_class + '  $context',
					'@param array $data',
			]
		))

		function_name = methodname[0] + methodname[1:]
		block.add_method(Phpmethod(
			function_name,
			body="""//Your block code
			return __('Hello Developer! This how to get the storename: %1 and this is the way to build a url: %2', $this->_storeManager->getStore()->getName(), $this->getUrl('contacts'));""",
			params=[],
			docstring=['@return string']
		))


		# Add plug first will add the module namespace to PhpClass
		self.add_class(block)

		block_template = '{}.phtml'.format(classname.replace('\\','/').lower())
		if layout_handle:
			# Layout Block XML
			xml_path = os.path.join('view', scope_name, 'layout')
			page = Xmlnode('page', attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:framework:View/Layout/etc/page_configuration.xsd"}, nodes=[
				Xmlnode('body', attributes={}, nodes=[
					Xmlnode(
						'referenceContainer' if reference_type == self.REFERENCE_CONTAINER else 'referenceBlock',
						attributes={
							'name': reference_name if reference_name else 'content'
						}, nodes=[
							Xmlnode('block', attributes={
								'class': block.class_namespace,
								'name': classname.replace('\\', '.').lower(),
								'as': classname.replace('\\', '_').lower(),
								'template': '{}::{}'.format(self.module_name, block_template),
							})
						]
					)
				])
			])
			xml_path = '{}/{}.xml'.format(xml_path,layout_handle.lower())
			self.add_xml(xml_path, page)

		# add template file
		path = os.path.join('view', scope_name, 'templates')
		self.add_static_file(path, StaticFile(
				block_template,
				body="""<?php
/**
 * @var $block \{classname}
 */
?>
<div>
	<?= $block->{function_name}() ?>
	<?= __('Hello {module_name}::{block_template}') ?>
</div>""".format(
					classname=block.class_namespace,
					function_name=function_name,
					module_name=self.module_name,
					block_template=block_template
				)
			)
		)

	@classmethod
	def params(cls):
		return [
			SnippetParam(name='classname', required=True,
				description='Example: Html\\Notices',
				regex_validator=r'^[\w\\]+$',
				error_message='Only alphanumeric, underscore and backslash characters are allowed'),
			SnippetParam(name='methodname', required=True,
				description='Example: displayDemoNotice',
				regex_validator= r'^\w+$',
				error_message='Only alphanumeric and underscore characters are allowed'),
			SnippetParam(name='scope', choises=cls.SCOPE_CHOISES, default=cls.SCOPE_FRONTEND),
			SnippetParam(name='layout_handle',
				description='Example: cms_index_index',
				regex_validator= r'^\w+$',
				error_message='Only alphanumeric and underscore characters are allowed'),
			SnippetParam(name='reference_type',
						 choises=cls.REFERENCE_CHOISES,
						 depend={'layout_handle': r'^\w+$'},
						 default=cls.REFERENCE_CONTAINER),
			SnippetParam(name='reference_name',
						 description='Example: content',
						 depend={'layout_handle': r'^\w+$'},
						 regex_validator=r'^[\w.]+$',
						 error_message='Only alphanumeric, dots and underscore characters are allowed'),
		]
		
