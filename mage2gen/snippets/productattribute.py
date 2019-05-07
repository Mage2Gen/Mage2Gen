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
from .. import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam
from ..utils import upperfirst

class ProductAttributeSnippet(Snippet):
	snippet_label = 'Product Attribute'

	FRONTEND_INPUT_TYPE = [
		("text","Text Field"),
		("textarea","Text Area"),
		("date","Date"),
		("boolean","Yes/No"),
		("multiselect","Multiple Select"),
		("select","Dropdown"),
		("price","Price"),
		("static","Static")
		#("media_image","Media Image"),
		#("weee","Fixed Product Tax"),
		#("swatch_visual","Visual Swatch"),
		#("swatch_text","Text Swatch")
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
		#"media_image":"",
		#"weee":"",
		#"swatch_visual":"",
		#"swatch_text":""
	}

	SCOPE_CHOICES = [
		("ScopedAttributeInterface::SCOPE_STORE","SCOPE_STORE"),
		("ScopedAttributeInterface::SCOPE_GLOBAL","SCOPE_GLOBAL"),
		("ScopedAttributeInterface::SCOPE_WEBSITE","SCOPE_WEBSITE")
	]

	APPLY_TO_CHOICES = [
		("-1","All Product Types"),
		("simple","Simple Products"),
		("grouped","Grouped Products"),
		("bundle","Bundled Products"),
		("configurable","Configurable Products"),
		("virtual","Virtual Products")
	]

	description = """
		Install Magento 2 product attributes programmatically. 

		The attribute is automatically added to all the attribute sets.
	"""

	def add(self, attribute_label, frontend_input='text', scope=1, required=False, upgrade_data=False, from_version='1.0.1', options=None, source_model=False, extra_params=None):
		extra_params = extra_params if extra_params else {}
		apply_to = extra_params.get('apply_to', [])
		try:
			apply_to = ','.join(x for x in apply_to if x != '-1')
		except:
			apply_to = ''

		value_type = self.FRONTEND_INPUT_VALUE_TYPE.get(frontend_input,'int')
		value_type = value_type if value_type != 'date' else 'datetime'
		user_defined = 'true'
		options = options.split(',') if options else []
		options_php_array = '"'+'","'.join(x.strip() for x in options) + '"'
		options_php_array_string = "array('values' => array("+options_php_array+"))"

		attribute_code = extra_params.get('attribute_code', None)
		if not attribute_code:
			attribute_code = attribute_label.lower().replace(' ','_')[:30]

		split_attribute_code = attribute_code.split('_')
		attribute_code_capitalized = ''.join(upperfirst(item) for item in split_attribute_code)

		if source_model and frontend_input in ['multiselect', 'select']:
			source_model = "\{}\{}\Model\Product\Attribute\Source\{}::class".format(self._module.package, self._module.name, attribute_code_capitalized)
			options_array = []
			for val in options:
				options_array.append("['value' => '" + val.lower() + "', 'label' => __('" + val + "')]")
			options_php_array = '[\n' + ',\n'.join(x.strip() for x in options_array) + '\n]'
			self.add_source_model(attribute_code_capitalized, options_php_array, extra_params.get('used_in_product_listing', False))
			options_php_array_string = "''"
		else:
			source_model = "''"

		templatePath = os.path.join(os.path.dirname(__file__), '../templates/attributes/productattribute.tmpl')

		with open(templatePath, 'rb') as tmpl:
			template = tmpl.read().decode('utf-8')

		is_swatch_option = frontend_input == 'swatch_visual' or frontend_input == 'swatch_text'

		if frontend_input == 'swatch_visual':
			options_php_array_string = "['values' => ['Black' => '#000000', 'White' => '#ffffff']]"
		elif frontend_input == 'swatch_text' :
			options_php_array_string = "['values' => ['Sample' => 'Sample']]"
		else:
			options_php_array_string = options_php_array_string

		methodBody = template.format(
			attribute_code=attribute_code,
			attribute_label=attribute_label,
			value_type=value_type,
			frontend_input=frontend_input,
			user_defined=user_defined,
			scope=scope,
			required = str(required).lower(),
			options = options_php_array_string,
			searchable = 'true' if extra_params.get('searchable', False) else 'false',
			filterable = 'true' if extra_params.get('filterable', False) else 'false',
			visible_on_front = 'true' if extra_params.get('visible_on_front', False) else 'false',
			comparable = 'true' if extra_params.get('comparable', False) else 'false',
			used_in_product_listing = 'true' if extra_params.get('used_in_product_listing', False) else 'false',
			unique = 'true' if extra_params.get('unique', False) else 'false',
			default = 'null',
			is_visible_in_advanced_search = extra_params.get('is_visible_in_advanced_search','0'),
			apply_to = apply_to,
			backend = 'Magento\Eav\Model\Entity\Attribute\Backend\ArrayBackend' if frontend_input == 'multiselect' else '',
			source_model = source_model,
			sort_order = '30',
			frontend = ''
		)

		setupType = 'Install'
		# TODO: add Upgrade Attribute Support
		if upgrade_data:
			setupType = 'Install'

		product_data = Phpclass('Setup\\ProductSetup'.format(setupType),
			extends='EavSetup',
			dependencies=[
				'Magento\\Eav\\Setup\\EavSetup',
				'Magento\\Catalog\\Model\\ResourceModel\\Product\\Attribute\Collection',
				'Magento\\Eav\\Model\\Entity\\Attribute\\ScopedAttributeInterface',
				'Magento\\Catalog\\Setup\\CategorySetup',
				'Magento\\Catalog\\Model\\ResourceModel\\Eav\\Attribute',
				'Magento\\Catalog\\Model\\ResourceModel\\Product'
			]
		)

		product_data.add_method(
			Phpmethod('getDefaultEntities',body="""
			return [\r
			    'catalog_product' => [
			        'entity_type_id' => CategorySetup::CATALOG_PRODUCT_ENTITY_TYPE_ID,
			        'entity_model' => Product::class,
			        'attribute_model' => Attribute::class,
			        'table' => 'catalog_product_entity',
			        'additional_attribute_table' => 'catalog_eav_attribute',
			        'entity_attribute_collection' =>
			        Collection::class,
			        'attributes' => [""",
					  end_body="""\r        ]\r    ]\r];\n"""))
		product_data.add_method(
			Phpmethod('getDefaultEntities', body=
			methodBody.replace('\n', '\r    ')))

		self.add_class(product_data)

		install_patch = Phpclass('Setup\\Patch\\Data\\{}ProductAttributes'.format(setupType),
			implements=['DataPatchInterface'],
			dependencies=[
				'Magento\\Framework\\Setup\\Patch\\DataPatchInterface',
				'Magento\\Framework\\Setup\\ModuleDataSetupInterface',
				'{}Factory'.format(product_data.class_namespace)
			],
			attributes=[
				'private $moduleDataSetup;',
				'private $productSetupFactory;'
			]
		)

		install_patch.add_method(Phpmethod(
			'__construct',
			params=[
				'ModuleDataSetupInterface $moduleDataSetup',
				'{}Factory $productSetupFactory'.format(product_data.class_name)
			],
			body="$this->moduleDataSetup = $moduleDataSetup;\n$this->productSetupFactory = $productSetupFactory;",
			docstring=[
				'Constructor',
				'',
				'@param ModuleDataSetupInterface $moduleDataSetup',
				'@param {}Factory $productSetupFactory'.format(product_data.class_name)
			]
		))

		install_patch.add_method(Phpmethod(
			'apply',
			body="""
		/** @var {class_name} $productSetup */
$productSetup = $this->productSetupFactory->create(['setup' => $this->moduleDataSetup]);
$productSetup->installEntities();""".format(class_name=product_data.class_name),
			docstring=[
				'Do Upgrade',
				'',
				'@return void'
			]
		))
		install_patch.add_method(Phpmethod(
			'getAliases',
			body="return [];",
			docstring=[
				'{@inheritdoc}'
			]
		))

		install_patch.add_method(Phpmethod(
			'getDependencies',
			access='public static',
			body="return [\n\n];",
			docstring=[
				'{@inheritdoc}'
			]
		))

		self.add_class(install_patch)

		# Catalog Attributes XML | Transport Attribute to Quote Item Product
		transport_to_quote_item = extra_params.get('transport_to_quote_item', False)
		if transport_to_quote_item:
			config = Xmlnode('config', attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Catalog:etc/catalog_attributes.xsd"}, nodes=[
				Xmlnode('group', attributes={'name': 'quote_item'}, nodes=[
					Xmlnode('attribute', attributes={
						'name': attribute_code
					})
				])
			])
			self.add_xml('etc/catalog_attributes.xml', config)

		etc_module = Xmlnode('config', attributes={
			'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Module/etc/module.xsd"}, nodes=[
			Xmlnode('module', attributes={'name': self.module_name}, nodes=[
				Xmlnode('sequence', attributes={}, nodes=[
					Xmlnode('module', attributes={'name': 'Magento_Catalog'})
				])
			])
		])
		self.add_xml('etc/module.xml', etc_module)

	def add_source_model(self, attribute_code_capitalized, options_php_array_string, used_in_product_listing):
		source_model = Phpclass('Model\\Product\\Attribute\Source\\{}'.format(upperfirst(attribute_code_capitalized)),
			extends='\\Magento\\Eav\\Model\\Entity\\Attribute\\Source\\AbstractSource')

		source_model.add_method(Phpmethod(
			'getAllOptions',
			body="$this->_options = " + options_php_array_string + ";\n"
				 "return $this->_options;",
			docstring=[
				'getAllOptions',
				'',
				'@return array'
			]
		))
		if used_in_product_listing:
			source_model.add_method(Phpmethod(
				'getFlatColumns',
				body="""
					$attributeCode = $this->getAttribute()->getAttributeCode();
					return [
						$attributeCode => [
							'unsigned' => false,
							'default' => null,
							'extra' => null,
							'type' => \Magento\Framework\DB\Ddl\Table::TYPE_TEXT,
							'length' => 255,
							'nullable' => true,
							'comment' => $attributeCode . ' column',
						],
					];""",
				docstring=[
					'@return array'
				]
			))
			source_model.add_method(Phpmethod(
				'getFlatIndexes',
				body="""
					$indexes = [];

					$index = 'IDX_' . strtoupper($this->getAttribute()->getAttributeCode());
					$indexes[$index] = ['type' => 'index', 'fields' => [$this->getAttribute()->getAttributeCode()]];
				
					return $indexes;
				""",
				docstring=[
					'@return array'
				]
			))
			source_model.add_method(Phpmethod(
				'getFlatUpdateSelect',
				params=['$store'],
				body="return $this->eavAttrEntity->create()->getFlatUpdateSelect($this->getAttribute(), $store);",
				docstring=[
					'@param int $store',
					'@return \Magento\Framework\DB\Select|null'
				]
			))
		self.add_class(source_model)

	@classmethod
	def params(cls):
		 return [
			 SnippetParam(
				name='attribute_label',
				required=True,
				description='Example: color',
				regex_validator= r'^[a-zA-Z\d\-_\s]+$',
				error_message='Only alphanumeric'),
			 SnippetParam(
				 name='frontend_input',
				 choises=cls.FRONTEND_INPUT_TYPE,
				 required=True,
				 default='text'),
			 SnippetParam(
				name='options',
				depend= {'frontend_input': r'select|multiselect'},
				required=False,
				description='Dropdown or Multiselect options comma seperated',
				error_message='Only alphanumeric'),
			 SnippetParam(
				 name='source_model',
				 depend={'frontend_input': r'select|multiselect'},
				 required=False,
				 default=False,
				 yes_no=True),
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
			 # TODO: add Upgrade Attribute Support
			 # SnippetParam(
				#  name='upgrade_data',
				#  default=False,
				#  yes_no=True
			 # ),
			 SnippetParam(
				 name='from_version',
				 description='1.0.1',
				 default='1.0.1'
			 ),
					  ]

	@classmethod
	def extra_params(cls):
		 return [
			SnippetParam(
				name='attribute_code',
				description='Default to lowercase of label',
				regex_validator= r'^[a-zA-Z]{1}\w{0,29}$',
				error_message='Only alphanumeric and underscore characters are allowed, and need to start with a alphabetic character. And can\'t be longer then 30 characters'),
			SnippetParam(
				 name='apply_to',
				 required=False,
				 default='',
				 choises=cls.APPLY_TO_CHOICES,
				 multiple_choices=True),
			SnippetParam(
				 name='searchable',
				 required=True,
				 default=False,
				 yes_no=True),
			 SnippetParam(
				 name='filterable',
				 required=True,
				 default=False,
				 depend= {'frontend_input': r'select|multiselect|price'},
				 yes_no=True),
			 SnippetParam(
				 name='visible_on_front',
				 required=True,
				 default=False,
				 yes_no=True),
			 SnippetParam(
				 name='comparable',
				 required=True,
				 default=False,
				 yes_no=True),
			 SnippetParam(
				 name='used_in_product_listing',
				 required=True,
				 default=False,
				 yes_no=True),
			 SnippetParam(
				 name='unique',
				 required=True,
				 default=False,
				 yes_no=True),
			 SnippetParam(
				 name='transport_to_quote_item',
				 required=True,
				 default=False,
				 yes_no=True),
		]
