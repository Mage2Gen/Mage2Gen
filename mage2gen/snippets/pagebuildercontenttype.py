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
from .. import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam, Readme
from ..utils import upperfirst


class PageBuilderContentTypeSnippet(Snippet):
	snippet_label = 'PageBuilder Content Type'



	description = """
	Page Builder comes with several content types (controls) you can use to build your storefront pages. In this tutorial, you will add a new content type: a Quote control, which you can use to show customer testimonials or other types of quotations within your storefront.
	
	https://devdocs.magento.com/page-builder/docs/create-custom-content-type/overview.html
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.count = 0


	def add(self, content_type_name, field_name, extra_params=None):
		# create layout.xml
		content_type_code = content_type_name.replace('_', '').lower()

		field_element_type = 'input'
		field_data_type = 'text'
		field_label = upperfirst(field_name)

		# form layout.xml
		self.add_xml('view/adminhtml/layout/pagebuilder_{}_{}_form.xml'.format(self._module.package.lower(), content_type_code),
			Xmlnode('page', attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:framework:View/Layout/etc/page_configuration.xsd"}, nodes=[
				Xmlnode('update', attributes={'handle': 'styles'}),
				Xmlnode('body', nodes=[
					Xmlnode('referenceContainer', attributes={'name': 'content'}, nodes=[
						Xmlnode('uiComponent', attributes={'name': 'pagebuilder_{}_{}_form'.format(self._module.package.lower(), content_type_code)})
					])
				])
			]))
		data_source = 'pagebuilder_{}_{}_form_data_source'.format(self._module.package.lower(), content_type_code)

		# form layout.xml
		self.add_xml('view/adminhtml/pagebuilder/content_type/{}_{}.xml'.format(self._module.package.lower(), content_type_code),
					 Xmlnode('config', attributes={
						 'xsi:noNamespaceSchemaLocation': "urn:magento:module:Magento_PageBuilder:etc/content_type.xsd"},
							 nodes=[
								 Xmlnode(
									 'type',
									 attributes={
										 'name': '{}_{}'.format(self._module.package.lower(), content_type_code),
										 'label': '{}'.format(content_type_code),
										 'menu_section': 'elements',
										 'components': 'Magento_PageBuilder/js/content-type',
										 'preview_component': 'Magento_PageBuilder/js/content-type/preview',
										 'master_component': 'Magento_PageBuilder/js/content-type/master',
										 'form': 'pagebuilder_{}_{}_form'.format(self._module.package.lower(), content_type_code),
										 'icon': 'icon-pagebuilder-image',
										 'sortOrder': '22',
										 'translate': 'label',
									 },
									 nodes=[
										 Xmlnode('children', attributes={'default_policy':'deny'}),
										 Xmlnode('appearances', nodes=[
											 Xmlnode('appearance', attributes={
												 'name': 'default',
												 'default': 'default',
												 'preview_template': '{}/content-type/{}/default/preview'.format(self.module_name, content_type_code),
												 'master_template': '{}/content-type/{}/default/master'.format(self.module_name, content_type_code),
												 'reader': 'Magento_PageBuilder/js/master-format/read/configurable',
											 }, nodes=[
												 Xmlnode('elements', nodes=[
													 Xmlnode('element', attributes={
														 'name': 'main',
													 },
															 nodes=[
																 Xmlnode('style', attributes={
																	 'name': 'text_align',
																	 'source': 'text_align',
																 }),
																 Xmlnode('attribute', attributes={
																	 'name': 'name',
																	 'source': 'data-content-type',
																 }),
																 Xmlnode('attribute', attributes={
																	 'name': 'appearance',
																	 'source': 'data-appearance',
																 }),
																 Xmlnode('css', attributes={
																	 'name': 'css_classes',
																 })
															 ]),
												 ]),
												 Xmlnode('element', attributes={
													 'name': '{}'.format(content_type_code),
												 },
														 nodes=[
															 Xmlnode('html', attributes={
																 'name': '{}'.format(content_type_code),
																 'converter': 'Magento_PageBuilder/js/converter/html/tag-escaper',
															 }),
														 ]),
											 ],
													 node_text='pagebuilder_{}_{}_form.{}'.format(
														 self._module.package.lower(), content_type_code, data_source)),
										 ]),

									]
							 )
				 	])
		 )




		# UI Component Form
		ui_form = Xmlnode('form', attributes={
			'xsi:noNamespaceSchemaLocation': "urn:magento:module:Magento_Ui:etc/ui_configuration.xsd",
			'extends':'pagebuilder_base_form'}, nodes=[
			Xmlnode('argument', attributes={'name': 'data', 'xsi:type': 'array'}, nodes=[
				Xmlnode('item', attributes={'name': 'js_config', 'xsi:type': 'array'}, nodes=[
					Xmlnode('item', attributes={'name': 'provider', 'xsi:type': 'string'},
							node_text='pagebuilder_{}_{}_form.{}'.format(self._module.package.lower(), content_type_code, data_source)),
				]),
				Xmlnode('item', attributes={'name': 'label', 'xsi:type': 'string', 'translate': 'true'},
						node_text='{}'.format(content_type_name)),
			]),
			Xmlnode('settings', nodes=[
				Xmlnode('namespace', node_text='pagebuilder_{}_{}_form'.format(self._module.package.lower(), content_type_code)),
				Xmlnode('deps', nodes=[
					Xmlnode('dep', node_text='pagebuilder_{}_{}_form.{}'.format(self._module.package.lower(), content_type_code, data_source))
				]),
			]),
			Xmlnode('dataSource', attributes={'name': data_source}, nodes=[
				Xmlnode('argument', attributes={'name': 'data', 'xsi:type': 'array'}, nodes=[
					Xmlnode('item', attributes={'name': 'js_config', 'xsi:type': 'array'}, nodes=[
						Xmlnode('item', attributes={'name': 'component', 'xsi:type': 'string'},
								node_text='Magento_Ui/js/form/provider'),
					]),
				]),
				Xmlnode('dataProvider', attributes={'name': data_source, 'class': 'Magento\PageBuilder\Model\ContentType\DataProvider'},
						nodes=[
							Xmlnode('settings', nodes=[
								Xmlnode('requestFieldName'),
								Xmlnode('primaryFieldName'),
							]),
						]),
			]),
			Xmlnode('fieldset', attributes={
				'name': 'appearance_fieldset',
				'sortOrder': '10',
				'component': 'Magento_PageBuilder/js/form/element/dependent-fieldset'
			}, nodes=[
				Xmlnode('settings', nodes=[
					Xmlnode('label', node_text='Appearance'),
					Xmlnode('additionalClasses', nodes=[
						Xmlnode('class', attributes={'name': 'admin__fieldset'}, node_text='true'),
					]),
					Xmlnode('collapsible', node_text='false'),
					Xmlnode('opened', node_text='true'),
					Xmlnode('imports', nodes=[
						Xmlnode('link', attributes={'name': 'hideFieldset'}, node_text='${$.name}.appearance:options'),
						Xmlnode('link', attributes={'name': 'hideLabel'}, node_text='${$.name}.appearance:options'),
					]),
				]),
				Xmlnode('field', attributes={'name': 'appearance', 'formElement': 'select',
											 'sortOrder': '10',
											 'component': 'Magento_PageBuilder/js/form/element/dependent-visual-select'},
						nodes=[
							Xmlnode('argument', attributes={'name': 'data', 'xsi:type': 'array'}, nodes=[
								Xmlnode('item', attributes={'name': 'config', 'xsi:type': 'array'}, nodes=[
									Xmlnode('item', attributes={'name': 'default', 'xsi:type': 'string'},
											node_text='default'),
								]),
							]),
							Xmlnode('settings', nodes=[
								Xmlnode('additionalClasses', nodes=[
									Xmlnode('class', attributes={'name': 'admin__fieldset-wide'}, node_text='true'),
									Xmlnode('class', attributes={'name': 'admin__field-visual-select-container'},
											node_text='true'),
								]),
								Xmlnode('dataType', node_text='text'),
								Xmlnode('validation', nodes=[
									Xmlnode('rule', attributes={'name': 'required-entry', 'xsi:type': 'boolean'},
											node_text='true'),
								]),
								Xmlnode('elementTmpl', node_text='Magento_PageBuilder/form/element/visual-select'),
							]),
						]),
				Xmlnode('formElements', nodes=[
					Xmlnode('select', nodes=[
						Xmlnode('settings', nodes=[
							Xmlnode('options', node_text='AppearanceSource{}'.format(upperfirst(content_type_name))),
						]),
					]),
				]),
				Xmlnode('fieldset', attributes={
					'name': 'general',
					'sortOrder': '20',
				}, nodes=[
					Xmlnode('settings', nodes=[
						Xmlnode('label', node_text='General'),
					]),
					Xmlnode('field',
							attributes={'name': '{}'.format(field_name), 'formElement': '{}'.format(field_element_type),
										'sortOrder': str(10 * self.count)},
							nodes=[
								Xmlnode('argument', attributes={'name': 'data', 'xsi:type': 'array'}, nodes=[
									Xmlnode('item', attributes={'name': 'config', 'xsi:type': 'array'}, nodes=[
										Xmlnode('item', attributes={'name': 'source', 'xsi:type': 'string'},
												node_text='page'),
									]),
								]),
								Xmlnode('settings', nodes=[
									Xmlnode('dataScope', node_text='{}'.format(field_name)),
									Xmlnode('dataType', node_text='{}'.format(field_data_type)),
									Xmlnode('label', attributes={'translate': 'false'},
											node_text='{}'.format(field_label)),
								]),
							]),
				]),
			]),
		])
		self.add_xml('view/adminhtml/ui_component/pagebuilder_{}_{}_form.xml'.format(self._module.package.lower(), content_type_code), ui_form)

		self.add_static_file('view/adminhtml/web/template/content-type/{}/default/'.format(content_type_code),
							 StaticFile('master.html', template_file='pagebuilder/master.tmpl', context_data={'field_name': field_name, 'content_type_code':content_type_code}))

		self.add_static_file('view/adminhtml/web/template/content-type/{}/default/'.format(content_type_code),
							 StaticFile('preview.html', template_file='pagebuilder/preview.tmpl', context_data={'field_name': field_name, 'content_type_code':content_type_code}))

		etc_module = Xmlnode('config', attributes={
			'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Module/etc/module.xsd"}, nodes=[
			Xmlnode('module', attributes={'name': self.module_name}, nodes=[
				Xmlnode('sequence', attributes={}, nodes=[
					Xmlnode('module', attributes={'name': 'Magento_PageBuilder'})
				])
			])
		])
		self.add_xml('etc/module.xml', etc_module)

	@classmethod
	def params(cls):
		return [
			SnippetParam(name='content_type_name', required=True,
				description='Example: FAQ',
				regex_validator=r'^[\w\\]+$',
				repeat=True,
				error_message='Only alphanumeric, underscore and backslash characters are allowed'),
			SnippetParam(
				required=True,
				name='field_name',
				description='Example: question',
				regex_validator=r'^[a-zA-Z]{1}\w{0,29}$',
				error_message='Only alphanumeric and underscore characters are allowed, and need to start with a alphabetic character. And can\'t be longer then 30 characters',
				repeat=True),
		]
		
