
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
from .. import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam, Readme
from ..utils import upperfirst

class CustomerAttributeSnippet(Snippet):
	snippet_label = 'Customer Attribute'

	FRONTEND_INPUT_TYPE = [
        ("text","Text Field"),
        ("textarea","Text Area"),
        ("date","Date"),
        ("boolean","Yes/No"),
        ("multiselect","Multiple Select"),
        ("select","Dropdown"),
    ]
	
	FRONTEND_INPUT_VALUE_TYPE = {
        "text":"varchar",
        "textarea":"text",
        "date":"datetime",
        "boolean":"int",
        "multiselect":"varchar",
        "select":"int",
    }

	USED_IN_FORMS = [
		('adminhtml_customer','adminhtml_customer'),	
		('adminhtml_checkout','adminhtml_checkout'),
		('customer_account_create','customer_account_create'),
		('customer_account_edit','customer_account_edit')
	]

	ADDRESS_USED_IN_FORMS = [
		('adminhtml_customer_address','adminhtml_customer_address'), 
		('customer_address_edit','customer_address_edit'), 
		('customer_register_address','customer_register_address')
	]

	CUSTOMER_ENTITY = [
		('customer','Customer'),
		('customer_address','Customer Address')
	]

	SOURCE_MODELS = [
		('Magento\Customer\Model\Customer\Attribute\Source\Group','Magento\Customer\Model\Customer\Attribute\Source\Group'),
		('Magento\Customer\Model\ResourceModel\Address\Attribute\Source\Country','Magento\Customer\Model\ResourceModel\Address\Attribute\Source\Country'),
		('Magento\Customer\Model\ResourceModel\Address\Attribute\Source\Region','Magento\Customer\Model\ResourceModel\Address\Attribute\Source\Region'),
		('','------------------'),
		('custom','Create Your own')
	]

	description ="""
		With this snippet you can create customer and customer address attribute programmatically thru a Magento 2 InstallData setup script. You can asign them to the forms where the should appear. 

		Warning. Not all template files are setup to load customer or customer address attributes dynamically. 

		Magento 2 create customer attribute programmatically
	"""

	def add(self,attribute_label, customer_forms=False, customer_address_forms=False, customer_entity='customer', frontend_input='text', checkout_billing=False, checkout_shipping=False, upgrade_data=False,
		from_version='1.0.1', static_field=False, required=False, source_model=False, source_model_options=False, extra_params=None):

		extra_params = extra_params if extra_params else {}
		attribute_code = extra_params.get('attribute_code', None)
		backend_model = ''
		
		if not attribute_code:
			attribute_code = attribute_label.lower().replace(' ','_')[:30]
		if frontend_input == 'select' and not source_model:
			source_model = "Magento\Customer\Model\ResourceModel\Address\Attribute\Source\Country"
		elif frontend_input == 'multiselect':
			backend_model = "Magento\Eav\Model\Entity\Attribute\Backend\ArrayBackend"
			if not source_model:    
				source_model = "Magento\Customer\Model\ResourceModel\Address\Attribute\Source\Country"
		elif frontend_input != 'multiselect' and frontend_input != 'select':
			source_model = ''
			backend_model = ''

		# customer source model
		if source_model == 'custom' and source_model_options and frontend_input == 'select' or frontend_input == 'multiselect':
			source_model_folder = 'Customer' if customer_entity =='customer' else 'Customer\\Address'
			source_model_class = Phpclass(
				'Model\\'+source_model_folder+'\\Attribute\\Source\\' + ''.join(n.capitalize() for n in attribute_code.split('_')),
				extends='\Magento\Eav\Model\Entity\Attribute\Source\AbstractSource'	
			)

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

		value_type = 'static' if static_field else self.FRONTEND_INPUT_VALUE_TYPE.get(frontend_input,'int')
		value_type = value_type if value_type != 'date' else 'datetime'

		forms_array = customer_forms if customer_entity == 'customer' else customer_address_forms
		forms_array = forms_array if forms_array else []
		forms_array = forms_array if isinstance(forms_array, list) else [forms_array]

		if forms_array:
			forms_php_array = "\n        '" + "',\n        '".join(forms_array) + "'\n    "
		elif customer_entity=='customer' and customer_forms==False:
			forms_php_array = "'adminhtml_customer','adminhtml_checkout','customer_account_create','customer_account_edit'"
		else :
			forms_php_array = None

		template = 'customerattribute.tmpl' if customer_entity=='customer' else 'customeraddressattribute.tmpl' 
		templatePath = os.path.join(os.path.dirname(__file__), '../templates/attributes/'+template)

		with open(templatePath, 'rb') as tmpl:
			template = tmpl.read().decode('utf-8')

		methodBody = template.format(
			attribute_code=attribute_code,
			attribute_label=attribute_label,
			value_type=value_type,
			frontend_input=frontend_input,
			required = str(required).lower(),
			sort_order = extra_params.get('sort_order','333') if extra_params.get('sort_order','333') else '333',
			visible =  'true' if extra_params.get('visible', True) else 'false',
			source_model = source_model,
			backend_model = backend_model
		)

		patchType = 'add'
		# TODO: add update Attribute Support
		if upgrade_data:
			patchType = 'add'

		split_attribute_code = attribute_code.split('_')
		attribute_code_capitalized = ''.join(upperfirst(item) for item in split_attribute_code)
		entity_type = 'Customer'
		entity_type_identifier = 'Magento\\Customer\\Model\\Customer'
		entity_type_alias='Customer'
		if customer_entity == 'customer_address':
			entity_type_identifier = 'Magento\\Customer\\Model\\Indexer\\Address\\AttributeProvider'
			entity_type_alias='AttributeProvider'
			entity_type = 'CustomerAddress'

		install_patch = Phpclass('Setup\\Patch\\Data\\{}{}{}Attribute'.format(patchType, attribute_code_capitalized, entity_type),
			 implements=['DataPatchInterface', 'PatchRevertableInterface'],
			 dependencies=[
				 'Magento\\Framework\\Setup\\Patch\\DataPatchInterface',
				 'Magento\\Framework\\Setup\\Patch\\PatchRevertableInterface',
				 'Magento\\Framework\\Setup\\ModuleDataSetupInterface',
				 'Magento\\Customer\\Setup\\CustomerSetupFactory',
				'Magento\\Customer\\Setup\\CustomerSetup',
				'Magento\\Eav\\Model\\Entity\\Attribute\\SetFactory',
				'Magento\\Eav\\Model\\Entity\\Attribute\\Set',
				 entity_type_identifier
			 ],
			 attributes=[
				 "/**\n\t * @var ModuleDataSetupInterface\n\t */\n\tprivate $moduleDataSetup;",
				 "/**\n\t * @var CustomerSetup\n\t */\n\tprivate $customerSetupFactory;",
				 "/**\n\t * @var SetFactory\n\t */\n\tprivate $attributeSetFactory;"
			 ]
		 )

		install_patch.add_method(Phpmethod(
			'__construct',
			params=[
				'ModuleDataSetupInterface $moduleDataSetup',
				'CustomerSetupFactory $customerSetupFactory',
				'SetFactory $attributeSetFactory'
			],
			body="$this->moduleDataSetup = $moduleDataSetup;\n$this->customerSetupFactory = $customerSetupFactory;\n$this->attributeSetFactory = $attributeSetFactory;",
			docstring=[
				'Constructor',
				'',
				'@param ModuleDataSetupInterface $moduleDataSetup',
				'@param CustomerSetupFactory $customerSetupFactory',
				'@param SetFactory $attributeSetFactory'
			]
		))


		methodBody = methodBody + "\n\n$attribute = $customerSetup->getEavConfig()->getAttribute({entity_type_alias}::ENTITY, '{attribute_code}');".format(entity_type_alias=entity_type_alias, attribute_code=attribute_code)
		if forms_php_array:
			attribute_form_data = "\n$attribute->addData([\n    'used_in_forms' => [{forms_php_array}]\n]);".format(customer_entity=customer_entity, attribute_code=attribute_code, forms_php_array=forms_php_array)
			methodBody = methodBody + attribute_form_data

		methodBody = methodBody + "\n$attribute->addData([\n    'attribute_set_id' => $attributeSetId,\n    'attribute_group_id' => $attributeGroupId\n\n]);\n$attribute->save();".format(entity_type_alias=entity_type_alias, attribute_code=attribute_code)

		install_patch.add_method(Phpmethod('apply',
			body_start='$this->moduleDataSetup->getConnection()->startSetup();',
			body_return='$this->moduleDataSetup->getConnection()->endSetup();',
			body="""
			/** @var CustomerSetup $customerSetup */
			$customerSetup = $this->customerSetupFactory->create(['setup' => $this->moduleDataSetup]);
			$customerEntity = $customerSetup->getEavConfig()->getEntityType({entity_type_alias}::ENTITY);
			$attributeSetId = $customerEntity->getDefaultAttributeSetId();

			/** @var $attributeSet Set */
			$attributeSet = $this->attributeSetFactory->create();
			$attributeGroupId = $attributeSet->getDefaultGroupId($attributeSetId);

			""".format(entity_type_alias=entity_type_alias) + methodBody,
			docstring=['{@inheritdoc}']))

		install_patch.add_method(Phpmethod(
			'revert',
			body_start='$this->moduleDataSetup->getConnection()->startSetup();',
			body_return='$this->moduleDataSetup->getConnection()->endSetup();',
			body="""
				/** @var CustomerSetup $customerSetup */
				$customerSetup = $this->customerSetupFactory->create(['setup' => $this->moduleDataSetup]);
				$customerSetup->removeAttribute(\Magento\Customer\Model\Customer::ENTITY, '{attribute_code}');""".format(
				attribute_code=attribute_code)
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

		extension_attributes_file = 'etc/extension_attributes.xml'

		api_class = "Magento\Customer\Api\Data\CustomerInterface"  if customer_entity=='customer' else 'Magento\Customer\Api\Data\AddressInterface'
	
		extension_attributes_xml = Xmlnode('config',attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:framework:Api/etc/extension_attributes.xsd"},nodes=[
			Xmlnode('extension_attributes',attributes={'for':api_class},match_attributes={'for'},nodes=[
				Xmlnode('attribute',attributes={
					'code':attribute_code,
					'type':'string'
				})
			])
		])

		self.add_xml(extension_attributes_file, extension_attributes_xml)

		etc_module_sequence = [
			Xmlnode('module', attributes={'name': 'Magento_Customer'})
		]
		if value_type == 'decimal':
			size = '\'12,4\''
		elif value_type == 'varchar' and not extra_params.get('field_size'):
			size = '255'
		else:
			size = 'null'

		attributes = {
			'name': "{}".format(attribute_code),
			'nullable': "true",
			'xsi:type': self.FRONTEND_INPUT_VALUE_TYPE.get(frontend_input,'int'),
			'comment': attribute_label
		}
		if size:
			attributes['length'] = size
		if value_type == 'integer' or value_type == 'bigint':
			attributes['xsi:type'] = "int"
		elif value_type == 'numeric':
			attributes['xsi:type'] = "real"

		if value_type in {'mallint', 'integer', 'bigint'}:
			attributes['identity'] = 'false'
			if extra_params.get('identity'):
				attributes['identity'] = 'true'
		if extra_params.get('field_size'):
			attributes['length'] = '{}'.format(extra_params.get('field_size'))
		elif value_type == 'decimal':
			attributes['scale'] = '4'
			attributes['precision'] = '12'
		elif value_type == 'varchar' and not extra_params.get('field_size'):
			attributes['length'] = '255'



		if static_field:
			# Create db_schema.xml declaration
			db_nodes = [
				Xmlnode('table', attributes={
					'name': "{}".format("customer_entity" if customer_entity == 'customer' else "customer_address_entity"),
				}, nodes=[
					Xmlnode('column', attributes=attributes)
				])
			]
			self.add_xml('etc/db_schema.xml', Xmlnode('schema', attributes={
				'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Setup/Declaration/Schema/etc/schema.xsd"},
													  nodes=db_nodes))

		if customer_entity =='customer_address' and (checkout_billing or checkout_shipping):
			self.add_composer_require("experius/module-extracheckoutaddressfields","*")

			# Create db_schema.xml declaration
			db_nodes = []
			for sales_entity in {'quote_address', 'sales_order_address'}:
				db_nodes.append(
					Xmlnode('table', attributes={
						'name': "{}".format(sales_entity),
					}, nodes=[
						Xmlnode('column', attributes=attributes)
					])
				)
			self.add_xml('etc/db_schema.xml', Xmlnode('schema', attributes={
				'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Setup/Declaration/Schema/etc/schema.xsd"},
													  nodes=db_nodes))

			fieldset_file = 'etc/fieldset.xml'

			fieldsets = []
			if checkout_shipping:
				fieldsets.append('extra_checkout_shipping_address_fields')
			if checkout_billing:
				fieldsets.append('extra_checkout_billing_address_fields')

			for fieldset in fieldsets:
				fieldset_xml = Xmlnode('config',
									   attributes={'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
												   'xsi:noNamespaceSchemaLocation': "urn:magento:framework:DataObject/etc/fieldset.xsd"},
									   nodes=[
										   Xmlnode('scope', attributes={'id': 'global'},
												   match_attributes={'id'}, nodes=[
												   Xmlnode('fieldset', attributes={
													   'id': fieldset
												   }, match_attributes={'id'}, nodes=[
													   Xmlnode('field', attributes={
														   'name': attribute_code
													   }, nodes=[
														   Xmlnode('aspect', attributes={
															   'name': 'to_order_address'
														   }),
														   Xmlnode('aspect', attributes={
															   'name': 'to_customer_address'
														   })
													   ])
												   ]),

											   ])
									   ])
				self.add_xml(fieldset_file, fieldset_xml)

			etc_module_sequence.append(
				Xmlnode('module', attributes={'name': 'Magento_Checkout'})
			)
			etc_module_sequence.append(
				Xmlnode('module', attributes={'name': 'Magento_Sales'})
			)

		etc_module = Xmlnode('config', attributes={
			'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Module/etc/module.xsd"}, nodes=[
			Xmlnode('module', attributes={'name': self.module_name}, nodes=[
				Xmlnode('sequence', attributes={}, nodes=etc_module_sequence)
			])
		])
		self.add_xml('etc/module.xml', etc_module)

		self.add_static_file(
			'.',
			Readme(
				attributes=" - {} - {} ({})".format(entity_type,attribute_label, attribute_code),
			)
		)

	def add_plugin(self, attribute_code, type='shipping'):
		classname = 'Magento\\Quote\\Model\\{}AddressManagement'.format(upperfirst(type))
		plugin = Phpclass('Plugin\\{}'.format(classname))

		split_attribute_code = attribute_code.split('_')
		attribute_code_capitalized = ''.join(upperfirst(item) for item in split_attribute_code)
		plugin.add_method(Phpmethod(
			'beforeAssign',
			body="""        $address->set{attribute_code_capitalized}($extAttributes->get{attribute_code_capitalized}());\n""".format(attribute_code_capitalized=attribute_code_capitalized),
			body_return='	} catch (\Exception $e) {\n			}\n		}\n		return [$cartId, $address];',
			body_start="""$extAttributes = $address->getExtensionAttributes();
        if (!empty($extAttributes)) {
            try {
        """,
			params=[
					  '\\{} $subject'.format(classname),
					   '$cartId',
					  '\\Magento\\Quote\\Api\\Data\\AddressInterface $address'
				   ] ,
			docstring=[
				'@param \\{} $subject'.format(classname),
				'@param $cartId',
				'\\Magento\\Quote\\Api\\Data\\AddressInterface $address',
				'@return array'
			]
		))

		# Add plug first will add the module namespace to PhpClass
		self.add_class(plugin)

		# Plugin XML
		config = Xmlnode('config', attributes={'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
											   'xsi:noNamespaceSchemaLocation': "urn:magento:framework:ObjectManager/etc/config.xsd"},
						 nodes=[
							 Xmlnode('type', attributes={'name': classname}, nodes=[
								 Xmlnode('plugin', attributes={
									 'name': plugin.class_namespace.replace('\\', '_'),
									 'type': plugin.class_namespace,
									 'sortOrder': '10',
									 'disabled': 'false'
								 })
							 ])
						 ])

		self.add_xml('etc/di.xml', config)

	@classmethod
	def params(cls):
		return [
             SnippetParam(
                name='customer_entity', 
                choises=cls.CUSTOMER_ENTITY,
                required=True,  
                default='customer',
				repeat=True),
             SnippetParam(
                name='attribute_label', 
                required=True, 
                description='Example: is_active',
                regex_validator= r'^[a-zA-Z\d\-_\s]+$',
                error_message='Only alphanumeric'),
             SnippetParam(
                name='customer_forms',
                choises=cls.USED_IN_FORMS,
                depend= {'customer_entity': r'^customer$'},
                default=['adminhtml_customer','adminhtml_checkout','customer_account_create','customer_account_edit'],
				multiple_choices=True,
                ),
             SnippetParam(
                name='customer_address_forms',
                choises=cls.ADDRESS_USED_IN_FORMS,
                depend= {'customer_entity': r'^customer_address$'}, 
                default=False,
				multiple_choices=True,
                ),
             SnippetParam(
                 name='required', 
                 default=False,
                 yes_no=True),
             SnippetParam(
                 name='frontend_input', 
                 choises=cls.FRONTEND_INPUT_TYPE,
                 required=True,  
                 default='text'),
             SnippetParam(
                name='source_model', 
                choises=cls.SOURCE_MODELS,
                depend= {'frontend_input': r'select|multiselect'}, 
                default='Magento\Customer\Model\Customer\Attribute\Source\Group'),
             SnippetParam(
                name='source_model_options',
                required=True,
                depend= {'source_model': r'custom'},
                description='Dropdown or Multiselect options comma seperated',
                error_message='Only alphanumeric'),
			SnippetParam(
				name='static_field',
				default=False,
				yes_no=True),
			# TODO: add Upgrade Attribute Support
			# SnippetParam(
			#  name='upgrade_data',
			#  default=False,
			#  yes_no=True
			# )
			SnippetParam(
				name='checkout_billing',
				default=False,
				depend={'customer_entity': r'^customer_address'},
				yes_no=True,
				description="requires experius/module-extracheckoutaddressfields"
			),
			SnippetParam(
				name='checkout_shipping',
				default=False,
				depend={'customer_entity': r'^customer_address'},
				yes_no=True,
				description="requires experius/module-extracheckoutaddressfields"
			)
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
				name='sort_order',
				description='333',
				regex_validator= r'^\d+$',
				error_message='Only numeric value'),
			SnippetParam(
				name='visible',
				default=True,
				yes_no=True),
			SnippetParam(
				name='field_size',
				description='Size of field, Example: 512 for max chars',
				required=False,
				regex_validator=r'^\d+$',
				error_message='Only numeric value allowed.',
				depend={'frontend_input': r'text|blob|decimal|numeric', },
				repeat=True
			),
		]
