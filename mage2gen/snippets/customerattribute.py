import os, locale
from mage2gen import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam

class CustomerAttributeSnippet(Snippet):
	snippet_label = 'Customer Attribute'

	FRONTEND_INPUT_TYPE = [
        ("text","Text Field"),
        ("textarea","Text Area"),
        ("date","Date"),
        ("boolean","Yes/No"),
        ("multiselect","Multiple Select"),
        ("select","Dropdown"),
        ("price","Price"),
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
        "price":"decimal",
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

	CUSTOMER_SOURCE_MODELS = [
		('Magento\Customer\Model\Customer\Attribute\Source\Group','Magento\Customer\Model\Customer\Attribute\Source\Group')
	]

	CUSTOMER_ADDRESS_SOURCE_MODELS = [
		('Magento\Customer\Model\ResourceModel\Address\Attribute\Source\Country','Magento\Customer\Model\ResourceModel\Address\Attribute\Source\Country'),
		('Magento\Customer\Model\ResourceModel\Address\Attribute\Source\Region','Magento\Customer\Model\ResourceModel\Address\Attribute\Source\Region')
	]

	meta_description = """

	"""

	description ="""
		magento 2 create customer attribute programmatically
    """

	def add(self,customer_entity,attribute_label,customer_forms,customer_address_forms,frontend_input,static_field_type,required=False,extra_params=None):

		attribute_code = attribute_label.lower().replace(' ','_');
		value_type = static_field_type if frontend_input=='static' else self.FRONTEND_INPUT_VALUE_TYPE.get(frontend_input,'int');
		source_model = "Magento\Customer\Model\ResourceModel\Address\Attribute\Source\Country" if frontend_input=='select' or frontend_input == 'multiselect' else 'Null'


		forms_php_array = ''

		forms_array = customer_forms if customer_entity == 'customer' else customer_address_forms

		if not isinstance(forms_array, list):
			forms_array = [forms_array]
		
		for form in forms_array:
			forms_php_array += "'"+form+"'," 

		forms_php_array =forms_php_array[:-1]


		template = 'customerattribute.tmpl' if customer_entity=='customer' else 'customeraddressattribute.tmpl' 
		templatePath = os.path.join(os.path.dirname(__file__), '../templates/attributes/'+template)

		with open(templatePath, 'rb') as tmpl:
			template = tmpl.read().decode('utf-8')

		methodBody = template.format(
			attribute_code=attribute_code,
			attribute_label=attribute_label,
			value_type=value_type,
			frontend_input=frontend_input,
			required = required,
			sort_order = extra_params.get('sort_order','333'),
			visible =  extra_params.get('visible','true'),
			source_model = source_model
		)

		install_data = Phpclass(
			'Setup\\InstallData',
			implements=['InstallDataInterface'],
			dependencies=[
				'Magento\\Framework\\Setup\\InstallDataInterface',
				'Magento\\Framework\\Setup\\ModuleContextInterface',
				'Magento\\Framework\\Setup\\ModuleDataSetupInterface',
				'Magento\\Customer\\Model\\Customer',
				'Magento\\Customer\\Setup\\CustomerSetupFactory'
				]
		)

		install_data.attributes.append('private $customerSetupFactory;')
		
		install_data.add_method(Phpmethod(
			'__construct',
			params=[
				'CustomerSetupFactory $customerSetupFactory'
			],
			body="$this->customerSetupFactory = $customerSetupFactory; \n$this->attributeSetFactory = $attributeSetFactory;"
		))

		install_data.add_method(Phpmethod('install',params=['ModuleDataSetupInterface $setup','ModuleContextInterface $context'],body="$customerSetup = $this->customerSetupFactory->create(['setup' => $setup]);"))
		install_data.add_method(Phpmethod('install',params=['ModuleDataSetupInterface $setup','ModuleContextInterface $context'],body=methodBody))

		attribute_form_data = "$attribute = $customerSetup->getEavConfig()->getAttribute('"+customer_entity+"', '"+attribute_code+"')->addData(['used_in_forms' => ["+forms_php_array+"]]);\n$attribute->save();"
		install_data.add_method(Phpmethod('install',params=['ModuleDataSetupInterface $setup','ModuleContextInterface $context'],body=attribute_form_data))

		self.add_class(install_data)	

		extension_attributes_file = 'etc/extension_attributes.xml'

		api_class = "Magento\Customer\Api\Data\CustomerInterface"  if customer_entity=='customer' else 'Magento\Customer\Api\Data\AddressInterface'

		print(api_class)
		print(customer_entity)
	
		extension_attributes_xml = Xmlnode('config',attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:framework:Api/etc/extension_attributes.xsd"},nodes=[
			Xmlnode('extension_attributes',attributes={'for':api_class},match_attributes={'for'},nodes=[
				Xmlnode('attribute',attributes={
					'code':attribute_code,
					'type':'string'
				})
			])
		])

		self.add_xml(extension_attributes_file, extension_attributes_xml)
			


	@classmethod
	def params(cls):
		return [
             SnippetParam(
                 name='customer_entity', 
                 choises=cls.CUSTOMER_ENTITY,
                 required=True,  
                 default='customer'),
             SnippetParam(
                name='attribute_label', 
                required=True, 
                description='Tab code. Example: catalog',
                regex_validator= r'^[a-z\d\-_\s]+$',
                error_message='Only alphanumeric'),
             SnippetParam(
                name='customer_forms',
                choises=cls.USED_IN_FORMS,
                depend= {'customer_entity': r'^customer$'}, 
                required=True, 
                ),
             SnippetParam(
                name='customer_address_forms',
                choises=cls.ADDRESS_USED_IN_FORMS,
                depend= {'customer_entity': r'^customer_address$'}, 
                required=True, 
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
                name='static_field_type',
                choises=cls.STATIC_FIELD_TYPES,
                depend= {'frontend_input': r'static'}, 
                required=True, 
                ),
         ]

	@classmethod
	def extra_params(cls):
		return []