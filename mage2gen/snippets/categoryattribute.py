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
import os, locale
from mage2gen import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam

class CategoryAttributeSnippet(Snippet):
	snippet_label = 'Category Attribute'

	FRONTEND_INPUT_TYPE = [
		("text","Text Field"),
		("textarea","Text Area"),
		("date","Date"),
		("boolean","Yes/No"),
		("multiselect","Multiple Select"),
		("select","Dropdown"),
		("price","Price"),
		("static","Static"),
		##("image","Image")
	]

	STATIC_FIELD_TYPES = [
		("varchar","Varchar"),
		("text","Text"),
		("int","Int"),
		("decimal","Decimal")
	]

	FRONTEND_INPUT_VALUE_TYPE = {
		"text":"varchar",
		"textarea":"text",
		"date":"date",
		"boolean":"int",
		"multiselect":"varchar",
		"select":"int",
		"price":"decimal",
		"image":"varchar"
	}

	FRONTEND_FORM_ELEMENT = {
		"text":"input",
		"textarea":"textarea",
		"checkbox":"checkbox",
		"select":"select",
		"multiselect":"multiselect",
		"date":"date",
		"image":"fileUploader"
	}

	SCOPE_CHOICES = [
		("0","SCOPE_STORE"),
		("1","SCOPE_GLOBAL"),
		("2","SCOPE_WEBSITE")
	]

	CATEGORY_SOURCE_MODELS = [
		('Magento\Eav\Model\Entity\Attribute\Source\Boolean','Magento\Eav\Model\Entity\Attribute\Source\Boolean'),
		('Magento\Catalog\Model\Category\Attribute\Source\Page','Magento\Catalog\Model\Category\Attribute\Source\Page'),
		('Magento\Catalog\Model\Category\Attribute\Source\Mode','Magento\Catalog\Model\Category\Attribute\Source\Mode'),
		('Magento\Catalog\Model\Category\Attribute\Source\Sortby','Magento\Catalog\Model\Category\Attribute\Source\Sortby'),
		('','------------------'),
		('custom','Create Your own')
	]

	CATEGORY_BACKEND_MODELS = [
		('Magento\Catalog\Model\Category\Attribute\Backend\Image','Magento\Catalog\Model\Category\Attribute\Backend\Image')
	]

	description = """
		Install Magento 2 category attributes programmatically. 
	"""
	
	def add(self,attribute_label, frontend_input='text', scope=1, required=False, source_model=False, source_model_options=False, extra_params=None):
		extra_params = extra_params if extra_params else {}
		
		value_type = self.FRONTEND_INPUT_VALUE_TYPE.get(frontend_input,'int')
		value_type = value_type if value_type != 'date' else 'datetime'

		form_element = self.FRONTEND_FORM_ELEMENT.get(frontend_input,'input')

		user_defined = 'false'
		backend_model = ''

		attribute_code = extra_params.get('attribute_code', None)
		if not attribute_code:
			attribute_code = attribute_label.lower().replace(' ','_')[:30]
		if frontend_input == 'select' and not source_model:
			source_model = "Magento\Eav\Model\Entity\Attribute\Source\Boolean"
		elif frontend_input == 'multiselect':
			backend_model = "Magento\Eav\Model\Entity\Attribute\Backend\ArrayBackend"
			if not source_model:    
				source_model = "Magento\Catalog\Model\Category\Attribute\Source\Page"
		elif frontend_input == "image":
			source_model = ''
			backend_model = "Magento\Catalog\Model\Category\Attribute\Backend\Image"
		elif frontend_input != 'multiselect' and frontend_input != 'select':
			source_model = ''
			backend_model = ''

		# customer source model
		if source_model == 'custom' and source_model_options and frontend_input == 'select' or frontend_input == 'multiselect':
			source_model_class = Phpclass(
				'Model\\Category\\Attribute\\Source\\' + ''.join(n.capitalize() for n in attribute_code.split('_')),
				extends='\Magento\Eav\Model\Entity\Attribute\Source\AbstractSource',
				attributes=[
					'protected $_optionsData;'
				]   
			)

			source_model_class.add_method(Phpmethod('__construct',
				params=['array $options'],
				body="$this->_optionsData = $options;",
				docstring=[
					'Constructor',
					'',
					'@param array $options',
				]
			))

			if frontend_input == 'select':
				to_option_array = "[\n        {}\n    ]".format(',\n        '.join(
					"['value' => '{1}', 'label' => __('{0}')]".format(value.strip(),index + 1) for index, value in enumerate(source_model_options.split(',')))
				)
			else:
				to_option_array = "[\n        {}\n    ]".format(',\n        '.join(
					"['value' => (string) '{0}', 'label' => __('{0}')]".format(value.strip()) for value in source_model_options.split(','))
				)
			

			source_model_class.add_method(Phpmethod('getAllOptions',
				body="""
				if ($this->_options === null) {{
				    $this->_options = {options};
				}}
				return $this->_options;
				""".format(options=to_option_array),
				docstring=[
					'getAllOptions',
					'',
					'@return array',
				]
			))
			self.add_class(source_model_class)

			source_model = source_model_class.class_namespace

		sort_order = extra_params.get('sort_order','333') if extra_params.get('sort_order','333') else '333'

		templatePath = os.path.join(os.path.dirname(__file__), '../templates/attributes/categoryattribute.tmpl')

		with open(templatePath, 'rb') as tmpl:
			template = tmpl.read().decode('utf-8')

		methodBody = template.format(
			attribute_code=attribute_code,
			attribute_label=attribute_label,
			value_type=value_type,
			frontend_input=frontend_input,
			user_defined = user_defined,
			scope = scope,
			required = str(required).lower(),
			default = 'null',
			sort_order = sort_order,
			source_model = source_model,
			backend_model = backend_model
		)

		install_data = Phpclass('Setup\\InstallData',
			implements=['InstallDataInterface'],
			dependencies=[
				'Magento\\Framework\\Setup\\InstallDataInterface',
				'Magento\\Framework\\Setup\\ModuleContextInterface',
				'Magento\\Framework\\Setup\\ModuleDataSetupInterface',
				'Magento\\Eav\\Setup\\EavSetup',
				'Magento\\Eav\\Setup\\EavSetupFactory'],
			attributes=[
				'private $eavSetupFactory;'
			])

		install_data.add_method(Phpmethod(
			'__construct',
			params=['EavSetupFactory $eavSetupFactory'],
			body="$this->eavSetupFactory = $eavSetupFactory;",
			docstring=[
				'Constructor',
				'',
				'@param \\Magento\\Eav\\Setup\\EavSetupFactory $eavSetupFactory'
			]
		)) 
		
		install_data.add_method(Phpmethod('install',
			params=['ModuleDataSetupInterface $setup','ModuleContextInterface $context'],
			body="$eavSetup = $this->eavSetupFactory->create(['setup' => $setup]);",
			docstring=['{@inheritdoc}']))
		install_data.add_method(Phpmethod('install',
			params=['ModuleDataSetupInterface $setup','ModuleContextInterface $context'],
			body=methodBody))
	
		self.add_class(install_data)

		category_form_file = 'view/adminhtml/ui_component/category_form.xml'

		if frontend_input=='select' or frontend_input == 'multiselect':
			options_xml = Xmlnode('item',attributes={'name':'options','xsi:type':'object'},node_text=source_model)
		else:
			options_xml = False

		if frontend_input == 'image' :
			image_xml = [
							Xmlnode('item',attributes={'name':'uploaderConfig','xsi:type':'array'},nodes=[Xmlnode('item',attributes={'name':'url','xsi:type':'url','path':'catalog/category_image/upload'})]),
							Xmlnode('item',attributes={'name':'elementTmpl','xsi:type':'string'},node_text='ui/form/element/uploader/uploader'),
							Xmlnode('item',attributes={'name':'previewTmpl','xsi:type':'string'},node_text='Magento_Catalog/image-preview')
						]
		
		else:
			image_xml = []    

		required_value = 'true' if required else 'false'
		required_xml = Xmlnode('item',attributes={'name':'required','xsi:type':'boolean'},node_text=required_value)
		required_entry_xml = Xmlnode('item',attributes={'name':'validation','xsi:type':'array'},nodes=[Xmlnode('item',attributes={'name':'required-entry','xsi:type':'boolean'},node_text=required_value)])

		item_xml = [
					required_xml,
					required_entry_xml,
					Xmlnode('item',attributes={'name':'sortOrder','xsi:type':'number',},node_text=sort_order),
					Xmlnode('item',attributes={'name':'dataType','xsi:type':'string'},node_text='string'),
					Xmlnode('item',attributes={'name':'formElement','xsi:type':'string'},node_text=form_element),
					Xmlnode('item',attributes={'name':'label','xsi:type':'string','translate':'true'},node_text=attribute_label)
				]

		item_xml.extend(image_xml)        

		category_form_xml = Xmlnode('form',attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Ui:etc/ui_configuration.xsd"},nodes=[
			Xmlnode('fieldset',attributes={'name':'general'},nodes=[
				# Xmlnode('argument',attributes={'name':'data','xsi:type':'array'},nodes=[
				#     Xmlnode('item',attributes={'name':'config','xsi:type':'array'},nodes=[
				#         Xmlnode('item',attributes={'name':'label','xsi:type':'string','translate':'true'},node_text='test'),
				#         Xmlnode('item',attributes={'name':'collapsible','xsi:type':'boolean'},node_text='true'),
				#         Xmlnode('item',attributes={'name':'sortOrder','xsi:type':'number'},node_text='100'),
				#     ])
				# ]),
				Xmlnode('field',attributes={'name':attribute_code},nodes=[
					Xmlnode('argument',attributes={'name':'data','xsi:type':'array'},nodes=[
						options_xml,                  
						Xmlnode('item',attributes={'name':'config','xsi:type':'array'},nodes=item_xml)
					])
				])
			])
		])

		self.add_xml(category_form_file, category_form_xml)
	
	@classmethod
	def params(cls):
		 return [
			 SnippetParam(
				name='attribute_label', 
				required=True, 
				description='Example: short_description',
				regex_validator= r'^[a-zA-Z\d\-_\s]+$',
				error_message='Only alphanumeric'),
			 SnippetParam(
				 name='frontend_input', 
				 choises=cls.FRONTEND_INPUT_TYPE,
				 required=True,  
				 default='text'),
			 SnippetParam(
				name='source_model', 
				choises=cls.CATEGORY_SOURCE_MODELS,
				depend= {'frontend_input': r'select|multiselect'}, 
				default='Magento\Eav\Model\Entity\Attribute\Source\Boolean'),
			 SnippetParam(
				name='source_model_options',
				required=True,
				depend= {'source_model': r'custom'},
				description='Dropdown or Multiselect options comma seperated',
				error_message='Only alphanumeric'),
			 SnippetParam(
				 name='scope',
				 required=True,  
				 choises=cls.SCOPE_CHOICES, 
				 default='1'),
			 SnippetParam(
				 name='required',
				 required=True,  
				 default=True,
				 yes_no=True),
		]

	@classmethod
	def extra_params(cls):
		 return [
			SnippetParam(
				name='attribute_code',
				description='Default to lowercase of label',
				regex_validator= r'^[a-zA-Z]{1}\w{0,29}$',
				error_message='Only alphanumeric and underscore characters are allowed, and need to start with a alphabetic character. And can\'t be longer then 30 characters'
			),
			SnippetParam(
				name='sort_order',
				description='333',
				regex_validator= r'^\d+$',
				error_message='Only numeric value'
			)
		 ]
