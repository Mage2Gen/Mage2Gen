# A Magento 2 module generator library
# Copyright (C) 2019 Mr. Lewis
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


class ViewModelSnippet(Snippet):

	description = """
	A ViewModel can be used to retrieve customer specific logic with in a template file.
	
	It is possible to set the viewModel argument with a layout update.
	"""

	def add(self, classname, methodname, layout_handle, reference_name='content', extra_params=None):
		# Add class
		classname = 'ViewModel\\{}'.format(classname)
		view_model = Phpclass(classname, '\\Magento\\Framework\\DataObject',
						 ['\\Magento\\Framework\\View\\Element\\Block\\ArgumentInterface'])
		scope_name = 'frontend'

		view_model.add_method(Phpmethod(
				'__construct',
				params=[
				],
				body="""parent::__construct();""",
				docstring=[
					'{} constructor.'.format(classname.split('\\')[-1]),
					'',
			]
		))

		function_name = methodname[0] + methodname[1:]
		view_model.add_method(Phpmethod(
			function_name,
			body="""//Your viewModel code
			// you can use me in your template like:
			// $viewModel = $block->getData('viewModel');
			// echo $viewModel->{}();
			
			return __('Hello Developer!');""".format(function_name),
			params=[],
			docstring=['@return string']
		))

		self.add_class(view_model)

		if layout_handle:
			# Layout Block XML
			xml_path = os.path.join('view', scope_name, 'layout')
			page = Xmlnode('page', attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:framework:View/Layout/etc/page_configuration.xsd"}, nodes=[
				Xmlnode('body', attributes={}, nodes=[
					Xmlnode(
						'referenceBlock',
						attributes={
							'name': reference_name if reference_name else 'example'
						}, nodes=[
							Xmlnode('arguments', attributes={},
								nodes=[
									Xmlnode('argument', attributes={
											'name': 'viewModel',
											'xsi:type': 'object',
										}, node_text='{}'.format(view_model.class_namespace)
									)
								]
							)
						]
					)
				])
			])
			xml_path = '{}/{}.xml'.format(xml_path,layout_handle.lower())
			self.add_xml(xml_path, page)

	@classmethod
	def params(cls):
		return [
			SnippetParam(name='classname', required=True,
				description='Example: Product\\Breadcrumbs',
				regex_validator=r'^[\w\\]+$',
				error_message='Only alphanumeric, underscore and backslash characters are allowed'),
			SnippetParam(name='methodname', required=True,
				description='Example: getProductName',
				regex_validator= r'^\w+$',
				error_message='Only alphanumeric and underscore characters are allowed'),
			SnippetParam(name='layout_handle',
				description='Example: catalog_product_view',
				regex_validator= r'^\w+$',
				error_message='Only alphanumeric and underscore characters are allowed',
				 required=True),
			SnippetParam(name='reference_name',
				 description='Example: breadcrumbs',
				 regex_validator=r'^[\w.]+$',
				 error_message='Only alphanumeric, dots and underscore characters are allowed'),
		]
		
