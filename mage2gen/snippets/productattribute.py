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
import os, locale, re
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
		("static","Static"),
		#("media_image","Media Image"),
		#("weee","Fixed Product Tax"),
		("swatch_visual","Visual Swatch"),
		("swatch_text","Text Swatch")
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
		"swatch_visual":"int",
		"swatch_text":"int"
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

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.is_default_added = False
		self.is_swatches_added = False

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
		options_php_array_string = "['values' => ["+options_php_array+"]]"
		version_number = re.sub("[^0-9]", "", from_version);

		attribute_code = extra_params.get('attribute_code', None)
		if not attribute_code:
			attribute_code = attribute_label.lower().replace(' ','_')[:30]

		if source_model and frontend_input in ['multiselect', 'select']:
			source_model = "\{}\{}\Model\Product\Attribute\Source\{}::class".format(self._module.package, self._module.name, upperfirst(attribute_code))
			options_array = []
			for val in options:
				options_array.append("['value' => '" + val.lower() + "', 'label' => __('" + val + "')]")
			options_php_array = '[\n' + ',\n'.join(x.strip() for x in options_array) + '\n]'
			self.add_source_model(attribute_code, options_php_array, extra_params.get('used_in_product_listing', False))
			options_php_array_string = ""
		else:
			source_model = "''"

		templatePath = os.path.join(os.path.dirname(__file__), '../templates/attributes/productattribute.tmpl')

		with open(templatePath, 'rb') as tmpl:
			template = tmpl.read().decode('utf-8')

		split_attribute_code = attribute_code.split('_')
		attribute_code_capitalized = ''.join(upperfirst(item) for item in split_attribute_code)
		attribute_code_capitalized_after = attribute_code_capitalized[0].lower() + attribute_code_capitalized[1:]

		is_swatch_option = frontend_input == 'swatch_visual' or frontend_input == 'swatch_text'

		if frontend_input == 'swatch_visual':
			options_php_array_string = "['values' => ['Black' => '#000000', 'White' => '#ffffff']]"
		elif frontend_input == 'swatch_text':
			options_php_array_string = "['values' => ['Sample' => 'Sample']]"
		else:
			options_php_array_string = options_php_array_string

		methodBody = template.format(
			attribute_code=attribute_code,
			attribute_label=attribute_label,
			value_type=value_type,
			frontend_input=frontend_input if not is_swatch_option else 'select',
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
				'Magento\\Catalog\\Model\\ResourceModel\\Product\\Attribute\\Collection',
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

		install_version = 'install' if not upgrade_data else 'upgrade' + version_number;

		if is_swatch_option:
			swatch_installer_model = Phpclass('Model\\Swatches',
				dependencies=[
					'Magento\\Eav\\Model\\ResourceModel\\Entity\\Attribute\\Option\\CollectionFactory as AttributeOptionCollectionFactory',
					'Magento\\Eav\\Model\\Config as EavModelConfig',
					'Magento\\Catalog\\Model\\ResourceModel\\Eav\\Attribute as eavAttribute'
				],
				attributes=[
					"protected $optionCollection = [];",
					"protected $colorMap = ['Black' => '#000000', 'White' => '#ffffff'];",
					"protected $attrOptionCollectionFactory;",
					"protected $eavConfig;"
				]
			)
			swatch_installer_model.add_method(Phpmethod(
				'__construct',
				params=[
					'CollectionFactory $attrOptionCollectionFactory',
					'EavModelConfig $eavConfig'
				],
				body="$this->attrOptionCollectionFactory = $attrOptionCollectionFactory;\n$this->eavConfig = $eavConfig;",
				docstring=[
					'Constructor',
					'',
					'@param AttributeOptionCollectionFactory $attrOptionCollectionFactory',
					'@param EavModelConfig $eavConfig',
				]
			))
			swatch_installer_model.add_method(Phpmethod(
				install_version,
				body="""$this->convert{attribute_code_capitalized}ToSwatches();
				""".format(
					attribute_code_capitalized=attribute_code_capitalized
				),
				docstring=[
					'{@inheritdoc}'
				]
			))
			swatch_installer_model.add_method(Phpmethod(
				'convert{}ToSwatches'.format(attribute_code_capitalized),
				body="""$attribute = $this->eavConfig->getAttribute('catalog_product', '{attribute_code}');
				if (!$attribute) {{
				    return;
				}}
				$attributeData['option'] = $this->addExistingOptions($attribute);
				$attributeData['frontend_input'] = 'select';
				$attributeData['swatch_input_type'] = '{visual_type}';
				$attributeData['update_product_preview_image'] = 1;
				$attributeData['use_product_image_for_swatch'] = 0;
				$attributeData['{key_option}'] = $this->getOptionSwatch($attributeData);
				$attributeData['{key_default}'] = $this->{get_default_option}($attributeData);
				$attributeData['{key_swatch}'] = $this->{get_option_swatch}($attributeData);
				$attribute->addData($attributeData);
				$attribute->save();
				""".format(
					attribute_code=attribute_code,
					visual_type='visual' if frontend_input == 'swatch_visual' else 'text',
					key_option='optionvisual' if frontend_input == 'swatch_visual' else 'optiontext',
					key_default='defaultvisual' if frontend_input == 'swatch_visual' else 'defaulttext',
					key_swatch='swatchvisual' if frontend_input == 'swatch_visual' else 'swatchtext',
					get_default_option='getOptionDefaultVisual' if frontend_input == 'swatch_visual' else 'getOptionDefaultText',
					get_option_swatch='getOptionSwatchVisual' if frontend_input == 'swatch_visual' else 'getOptionSwatchText',
				),
				docstring=[
					'Convert {} to swatches'.format(attribute_code)
				]
			))
			swatch_installer_model.add_method(Phpmethod(
				'getOptionSwatch',
				params=['array $attributeData'],
				body="""$optionSwatch = ['order' => [], 'value' => [], 'delete' => []];
				$i = 0;
				foreach ($attributeData['option'] as $optionKey => $optionValue) {
				    $optionSwatch['delete'][$optionKey] = '';
				    $optionSwatch['order'][$optionKey] = (string)$i++;
				    $optionSwatch['value'][$optionKey] = [$optionValue, ''];
				}
				return $optionSwatch;
				""",
				docstring=[
					'@param array $attributeData',
					'@return array'
				]
			))
			swatch_installer_model.add_method(Phpmethod(
				'getOptionSwatchVisual',
				access='private',
				params=['array $attributeData'],
				body="""$optionSwatch = ['value' => []];
				foreach ($attributeData['option'] as $optionKey => $optionValue) {
				    if (substr($optionValue, 0, 1) == '#' && strlen($optionValue) == 7) {
				        $optionSwatch['value'][$optionKey] = $optionValue;
				    } else if ($this->colorMap[$optionValue]) {
				        $optionSwatch['value'][$optionKey] = $this->colorMap[$optionValue];
				    } else {
				        $optionSwatch['value'][$optionKey] = $this->colorMap['White'];
				    }
				}
				return $optionSwatch;
				""",
				docstring=[
					'@param array $attributeData',
					'@return array'
				]
			))
			swatch_installer_model.add_method(Phpmethod(
				'getOptionDefaultVisual',
				access='private',
				params=['array $attributeData'],
				body="""$optionSwatch = $this->getOptionSwatchVisual($attributeData);
				return [array_keys($optionSwatch['value'])[0]];
				""",
				docstring=[
					'@param array $attributeData',
					'@return array'
				]
			))
			swatch_installer_model.add_method(Phpmethod(
				'getOptionSwatchText',
				access='private',
				params=['array $attributeData'],
				body="""$optionSwatch = ['value' => []];
				foreach ($attributeData['option'] as $optionKey => $optionValue) {
				    $optionSwatch['value'][$optionKey] = [$optionValue, ''];
				}
				return $optionSwatch;
				""",
				docstring=[
					'@param array $attributeData',
					'@return array'
				]
			))
			swatch_installer_model.add_method(Phpmethod(
				'getOptionDefaultText',
				access='private',
				params=['array $attributeData'],
				body="""$optionSwatch = $this->getOptionSwatchText($attributeData);
				return [array_keys($optionSwatch['value'])[0]];
				""",
				docstring=[
					'@param array $attributeData',
					'@return array'
				]
			))
			swatch_installer_model.add_method(Phpmethod(
				'loadOptionCollection',
				access='private',
				params=['$attributeId'],
				body="""if (empty($this->optionCollection[$attributeId])) {
				    $this->optionCollection[$attributeId] = $this->attrOptionCollectionFactory->create()
				        ->setAttributeFilter($attributeId)
				        ->setPositionOrder('asc', true)
				        ->load();
				}
				""",
				docstring=[
					'@param $attributeId',
					'@return void'
				]
			))
			swatch_installer_model.add_method(Phpmethod(
				'addExistingOptions',
				access='private',
				params=['eavAttribute $attribute'],
				body="""$options = [];
				$attributeId = $attribute->getId();
				if ($attributeId) {
				    $this->loadOptionCollection($attributeId);
				    /** @var \Magento\Eav\Model\Entity\Attribute\Option $option */
				    foreach ($this->optionCollection[$attributeId] as $option) {
				        $options[$option->getId()] = $option->getValue();
				    }
				}
				return $options;
				""",
				docstring=[
					'@param eavAttribute $attribute',
					'@return array'
				]
			))
			self.add_class(swatch_installer_model)

			product_data = Phpclass('Setup\\ProductSetup'.format(setupType),
				extends='EavSetup',
				dependencies=[
					'Magento\\Eav\\Setup\\EavSetup',
					'Magento\\Catalog\\Model\\ResourceModel\\Product\\Attribute\\Collection',
					'Magento\\Eav\\Model\\Entity\\Attribute\\ScopedAttributeInterface',
					'Magento\\Catalog\\Setup\\CategorySetup',
					'Magento\\Catalog\\Model\\ResourceModel\\Eav\\Attribute',
					'Magento\\Catalog\\Model\\ResourceModel\\Product',
					'Magento\\Eav\Model\\Entity\Setup\\Context',
					'Magento\\Eav\Model\\ResourceModel\\Entity\\Attribute\\Group\\CollectionFactory',
					'Magento\\Framework\\App\\CacheInterface',
					'Magento\\Framework\\Setup\\ModuleDataSetupInterface',
					'{}'.format(swatch_installer_model.class_namespace)
				],
				attributes=[
					"protected $swatches;"
				]
			)

		if is_swatch_option:
			install_patch = Phpclass('Setup\\Patch\\Data\\{}ProductAttributes'.format(setupType),
				implements=['DataPatchInterface'],
				dependencies=[
					'Magento\\Framework\\Setup\\Patch\\DataPatchInterface',
					'Magento\\Framework\\Setup\\ModuleDataSetupInterface',
					'{}'.format(swatch_installer_model.class_namespace),
					'{}Factory'.format(product_data.class_namespace)
				],
				attributes=[
					'private $moduleDataSetup;',
					'private $productSetupFactory;',
					'protected $swatches;'
				]
			)
			install_patch.add_method(Phpmethod(
				'__construct',
				params=[
					'ModuleDataSetupInterface $moduleDataSetup',
					'{} $swatches'.format(swatch_installer_model.class_name),
					'{}Factory $productSetupFactory'.format(product_data.class_name)
				],
				body="""
				$this->moduleDataSetup = $moduleDataSetup;
				$this->swatches = $swatches;
				$this->productSetupFactory = $productSetupFactory;
				""",
				docstring=[
					'Constructor',
					'',
					'@param ModuleDataSetupInterface $moduleDataSetup',
					'@param {} $swatches'.format(swatch_installer_model.class_name),
					'@param {}Factory $productSetupFactory'.format(product_data.class_name)
				]
			))
			if self.is_default_added == False:
				install_patch.add_method(Phpmethod(
					'apply',
					body="""
						/** @var {class_name} $productSetup */
						$productSetup = $this->productSetupFactory->create(['setup' => $this->moduleDataSetup]);
						$productSetup->installEntities();
						$this->swatches->{install_version}();
						""".format(class_name=product_data.class_name, install_version=install_version),
					docstring=[
						'Do Upgrade',
						'',
						'@return void'
					]
				))
			else:
				install_patch.add_method(Phpmethod(
					'apply',
					body="""
						$this->swatches->{install_version}();
						""".format(install_version=install_version),
					docstring=[
						'Do Upgrade',
						'',
						'@return void'
					]
				))
			self.is_swatches_added = True;
		else:
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


		if self.is_swatches_added == False:
			install_patch.add_method(Phpmethod(
				'apply',
				body="""
					/** @var {class_name} $productSetup */
					$productSetup = $this->productSetupFactory->create(['setup' => $this->moduleDataSetup]);
					$productSetup->installEntities();
					""".format(class_name=product_data.class_name),
				docstring=[
					'Do Upgrade',
					'',
					'@return void'
				]
			))
			self.is_default_added = True;

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

	def add_source_model(self, attribute_code, options_php_array_string, used_in_product_listing):
		source_model = Phpclass('Model\\Product\\Attribute\Source\\{}'.format(upperfirst(attribute_code)),
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
