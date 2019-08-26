
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

class CustomerAttributeSnippet(Snippet):
	snippet_label = 'Customer Attribute'

	FRONTEND_INPUT_TYPE = [
        ("text","Text Field"),
        ("textarea","Text Area"),
        ("date","Date"),
        ("boolean","Yes/No"),
        ("multiselect","Multiple Select"),
        ("select","Dropdown"),
        ("static","Static")
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
		from_version='1.0.1', static_field_type='varchar', required=False, source_model=False, source_model_options=False, extra_params=None):

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

		value_type = static_field_type if frontend_input=='static' else self.FRONTEND_INPUT_VALUE_TYPE.get(frontend_input,'int')
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
		if customer_entity == 'customer_address':
			entity_type = 'CustomerAddress'

		install_patch = Phpclass('Setup\\Patch\\Data\\{}{}{}Attribute'.format(patchType, attribute_code_capitalized, entity_type),
			 implements=['DataPatchInterface', 'PatchRevertableInterface'],
			 dependencies=[
				 'Magento\\Framework\\Setup\\Patch\\DataPatchInterface',
				 'Magento\\Framework\\Setup\\Patch\\PatchRevertableInterface',
				 'Magento\\Framework\\Setup\\ModuleDataSetupInterface',
				 'Magento\\Customer\\Setup\\CustomerSetupFactory',
				'Magento\\Customer\\Setup\\CustomerSetup'
			 ],
			 attributes=[
				 "/**\n\t * @var ModuleDataSetupInterface\n\t */\n\tprivate $moduleDataSetup;",
				 "/**\n\t * @var CustomerSetup\n\t */\n\tprivate $customerSetupFactory;"
			 ]
		 )

		install_patch.add_method(Phpmethod(
			'__construct',
			params=[
				'ModuleDataSetupInterface $moduleDataSetup',
				'CustomerSetupFactory $customerSetupFactory'
			],
			body="$this->moduleDataSetup = $moduleDataSetup;\n$this->customerSetupFactory = $customerSetupFactory;",
			docstring=[
				'Constructor',
				'',
				'@param ModuleDataSetupInterface $moduleDataSetup',
				'@param CustomerSetupFactory $customerSetupFactory'
			]
		))


		if forms_php_array:
			attribute_form_data = "\n\n$attribute = $customerSetup->getEavConfig()->getAttribute('{customer_entity}', '{attribute_code}')->addData([\n    'used_in_forms' => [{forms_php_array}]\n]);\n$attribute->save();".format(customer_entity=customer_entity, attribute_code=attribute_code, forms_php_array=forms_php_array)
			methodBody = methodBody + attribute_form_data

		install_patch.add_method(Phpmethod('apply',
			body_start='$this->moduleDataSetup->getConnection()->startSetup();',
			body_return='$this->moduleDataSetup->getConnection()->endSetup();',
			body="""
			/** @var CustomerSetup $customerSetup */
			$customerSetup = $this->customerSetupFactory->create(['setup' => $this->moduleDataSetup]);
			""" + methodBody,
			docstring=['{@inheritdoc}']))

		install_patch.add_method(Phpmethod(
			'revert',
			body_start='$this->moduleDataSetup->getConnection()->startSetup();',
			body_return='$this->moduleDataSetup->getConnection()->endSetup();',
			body="""
				/** @var CustomerSetup $customerSetup */
				$customerSetup = $this->eavSetupFactory->create(['setup' => $this->moduleDataSetup]);
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

		if customer_entity =='customer_address' and (checkout_billing or checkout_shipping):
			self.add_static_file('view/frontend/web/js/action',
								 StaticFile('create-shipping-address-mixin.js', template_file='attributes/customer/address/create-shipping-address-mixin.tmpl'))
			self.add_static_file('view/frontend/web/js/action',
								 StaticFile('set-billing-address-mixin.js',
											template_file='attributes/customer/address/set-billing-address-mixin.tmpl'))
			self.add_static_file('view/frontend/web/js/action',
								 StaticFile('set-shipping-information-mixin.js',
											template_file='attributes/customer/address/set-shipping-information-mixin.tmpl'))
			self.add_static_file('view/frontend',
								 StaticFile('requirejs-config.js',
											template_file='attributes/customer/address/requirejs-config.tmpl',
											context_data={'module_name': self.module_name}))

			layout_processor = Phpclass(
				'Block\\Checkout\\LayoutProcessor',
				implements=['\Magento\Checkout\Block\Checkout\LayoutProcessorInterface']
			)

			methodBody = "\n"
			additionalFieldsBody = "\n"
			if checkout_shipping:
				self.add_plugin(attribute_code)
				methodBody += "		$result = $this->getShippingFormFields($result);\n"
				additionalFieldsBody += "		$shippingAttributes[] = '{}';\n".format(attribute_code)
				layout_processor.add_method(Phpmethod('getShippingFormFields',
						  body_return="return $result;",
						  params=[
							  '$result'
						  ],
						  body=""" if(isset($result['components']['checkout']['children']['steps']['children']
    ['shipping-step']['children']['shippingAddress']['children']
    ['shipping-address-fieldset'])
) {
	    $customShippingFields = $this->getFields('shippingAddress.custom_attributes','shipping');

	    $shippingFields = $result['components']['checkout']['children']['steps']['children']
	    ['shipping-step']['children']['shippingAddress']['children']
	    ['shipping-address-fieldset']['children'];

	    $shippingFields = array_replace_recursive($shippingFields,$customShippingFields);

	    $result['components']['checkout']['children']['steps']['children']
	    ['shipping-step']['children']['shippingAddress']['children']
	    ['shipping-address-fieldset']['children'] = $shippingFields;
}"""
						  )
				)
			if checkout_billing:
				self.add_plugin(attribute_code, 'billing')
				methodBody += "		$result = $this->getBillingFormFields($result);\n"
				additionalFieldsBody += "		$billingAttributes[] = '{}';\n".format(attribute_code)
				layout_processor.add_method(Phpmethod('getBillingFormFields',
													  body_return="return $result;",
													  params=[
														  '$result'
													  ],
													  body=""" if(isset($result['components']['checkout']['children']['steps']['children']
    ['billing-step']['children']['payment']['children']
    ['payments-list'])
) {
	    $paymentForms = $result['components']['checkout']['children']['steps']['children']
	    ['billing-step']['children']['payment']['children']
	    ['payments-list']['children'];

	    foreach ($paymentForms as $paymentMethodForm => $paymentMethodValue) {

	        $paymentMethodCode = str_replace('-form', '', $paymentMethodForm);

	        if (!isset($result['components']['checkout']['children']['steps']['children']['billing-step']['children']['payment']['children']['payments-list']['children'][$paymentMethodCode . '-form'])) {
	            continue;
	        }

	        $billingFields = $result['components']['checkout']['children']['steps']['children']
	        ['billing-step']['children']['payment']['children']
	        ['payments-list']['children'][$paymentMethodCode . '-form']['children']['form-fields']['children'];

	        $customBillingFields = $this->getFields('billingAddress' . $paymentMethodCode . '.custom_attributes','billing');

	        $billingFields = array_replace_recursive($billingFields, $customBillingFields);

	        $result['components']['checkout']['children']['steps']['children']
	        ['billing-step']['children']['payment']['children']
	        ['payments-list']['children'][$paymentMethodCode . '-form']['children']['form-fields']['children'] = $billingFields;
	}
}"""
													  )
											)

			layout_processor.add_method(Phpmethod('process',
				  body=methodBody,
				  body_return="return $result;",
				  params=[
					  '$result'
				  ]
				)
			)

			layout_processor.add_method(Phpmethod('getFields',
					  body="""$fields = [];
	foreach($this->getAdditionalFields($addressType) as $field){
	    $fields[$field] = $this->getField($field,$scope);
	}""",
					  body_return="return $fields;",
					  params=[
						  '$scope',
						  '$addressType'
					  ]
					  )
			)

			layout_processor.add_method(Phpmethod('getField',
												  body="""$field = [
	    'config' => [
	        'customScope' => $scope,
	        'template' => 'ui/form/field',
	        'elementTmpl' => 'ui/form/element/input'
	    ],
	    'dataScope' => $scope . '.' . $attributeCode,
	    'sortOrder' => '{sort_order}',
	    'visible' => true,
	    'provider' => 'checkoutProvider',
	    'validation' => [],
	    'options' => [],
	    'label' => __('{attribute_label}')
];""".format(sort_order=extra_params.get('sort_order','333') if extra_params.get('sort_order','333') else '333',attribute_label=attribute_label),
					  body_return="return $field;",
					  params=[
						  '$attributeCode',
						  '$scope'
					  ]
					  )
			)

			layout_processor.add_method(Phpmethod('getAdditionalFields',
					  body_return="return $addressType == 'shipping' ? $shippingAttributes : $billingAttributes; ",
					  body_start="""$shippingAttributes = [];
        $billingAttributes = [];""",
					  body=additionalFieldsBody,
					  params=[
						  "$addressType='shipping'"
					  ]
					  )
			)


			# add checkout filed
			frontend_di_xml = Xmlnode('config',
				attributes={'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance', 'xsi:noNamespaceSchemaLocation': "urn:magento:framework:ObjectManager/etc/config.xsd"},
				nodes=[
				   Xmlnode('type', attributes={'name': 'Magento\Checkout\Block\Onepage'},nodes=[
						   Xmlnode('arguments', attributes={}, nodes=[
							   Xmlnode('argument', attributes={'name': 'layoutProcessors', 'xsi:type':'array'}, nodes=[
								   Xmlnode('item', attributes={'name': '{}_extra_checkout_address_fields_layoutprocessor'.format(self._module.package.lower()), 'xsi:type': 'object'},
										   node_text='{}\\{}\\{}'.format(self._module.package,self._module.name, layout_processor.class_namespace)
								   )
							   ])
						   ])
					   ])
				])
			etc_module_sequence.append(
				Xmlnode('module', attributes={'name': 'Magento_Checkout'})
			)
			self.add_xml('etc/frontend/di.xml', frontend_di_xml)
			self.add_class(layout_processor)

		etc_module = Xmlnode('config', attributes={
			'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Module/etc/module.xsd"}, nodes=[
			Xmlnode('module', attributes={'name': self.module_name}, nodes=[
				Xmlnode('sequence', attributes={}, nodes=etc_module_sequence)
			])
		])
		self.add_xml('etc/module.xml', etc_module)

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
                 default=True,
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
                name='static_field_type',
                choises=cls.STATIC_FIELD_TYPES,
                default='varchar',
                depend= {'frontend_input': r'static'}, 
                required=True,
                ),
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
				yes_no=True
			),
			SnippetParam(
				name='checkout_shipping',
				default=False,
				depend={'customer_entity': r'^customer_address'},
				yes_no=True
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
		]
