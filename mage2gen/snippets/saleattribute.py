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
import os, locale
from .. import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam
from ..utils import upperfirst


class SalesAttributeSnippet(Snippet):
	snippet_label = 'Sales Attribute'

	FRONTEND_INPUT_TYPE = [
		("text", "Text Field"),
		("textarea", "Text Area"),
		("date", "Date"),
		# ("boolean", "Yes/No"),
		# ("multiselect", "Multiple Select"),
		# ("select", "Dropdown"),
	]

	FRONTEND_INPUT_VALUE_TYPE = {
		"text": "varchar",
		"textarea": "text",
		"date": "date",
		"boolean": "int",
		"multiselect": "varchar",
		"select": "int",
	}

	SALES_ENTITIES = [
		("quote", "Quote"),
		("quote_item", "Quote Item"),
		("quote_address", "Quote Address"),
		# ("quote_address_item", "Quote Address Item"),
		# ("quote_address_rate", "Quote Address Rate"),
		("order", "Order"),
		# ("order_payment", "Order Payment"),
		("order_item", "Order Item"),
		("order_address", "Order Address"),
		# ("order_status_history", "Order Status History"),
		("invoice", "Invoice"),
		("invoice_item", "Invoice Item"),
		# ("invoice_comment", "Invoice Comment"),
		("creditmemo", "Creditmemo"),
		("creditmemo_item", "Creditmemo Item"),
		# ("creditmemo_comment", "Creditmemo Comment"),
		("shipment", "Shipment"),
		("shipment_item", "Shipment Item"),
		# ("shipment_track", "Shipment Track"),
		# ("shipment_comment", "Shipment Comment"),
	]

	description = """
		Install Magento 2 sales order attributes programmatically.
	"""
	
	def add(self, attribute_label, sales_entity='quote', frontend_input='varchar', required=False, upgrade_data=False, from_version='1.0.1', extra_params=None):
		extra_params = extra_params if extra_params else {}
		value_type = self.FRONTEND_INPUT_VALUE_TYPE.get(frontend_input)

		setup_type = 'sales'
		if sales_entity.__contains__('quote'):
			setup_type = 'quote'

		attribute_code = extra_params.get('attribute_code', None)
		if not attribute_code:
			attribute_code = attribute_label.lower().replace(' ','_')[:30]

		if extra_params.get('field_size') :
			size = extra_params.get('field_size')
		elif value_type=='decimal':
			size = '\'12,4\''
		elif value_type=='varchar' and not extra_params.get('field_size'):
			size = '255'
		else:
			size = 'null'

		templatePath = os.path.join(os.path.dirname(__file__), '../templates/attributes/sales/attribute.tmpl')

		with open(templatePath, 'rb') as tmpl:
			template = tmpl.read().decode('utf-8')

		methodBody = template.format(
			attribute_code=attribute_code,
			setup_type=setup_type,
			sales_entity=sales_entity,
			type=value_type,
			length=size,
			visible='true' if extra_params.get('visible', False) else 'false',
			required='true' if required else 'false',
			grid='true' if extra_params.get('used_in_admin_grid', False) else 'false'
		)

		setupType = 'Install'
		if upgrade_data:
			setupType = 'Upgrade'

		install_data = Phpclass('Setup\\{}Data'.format(setupType),
			implements=['{}DataInterface'.format(setupType)],
			dependencies=[
				'Magento\\Framework\\Setup\\{}DataInterface'.format(setupType),
				'Magento\\Framework\\Setup\\ModuleContextInterface',
				'Magento\\Framework\\Setup\\ModuleDataSetupInterface',
				'Magento\\{setup_type_class}\\Setup\\{setup_type_class}SetupFactory'.format(setup_type_class=upperfirst(setup_type))],
			attributes=['private ${}SetupFactory;'.format(setup_type)])

		install_data.add_method(Phpmethod(
			'__construct',
			params=[
				'{setup_type_class}SetupFactory ${setup_type}SetupFactory'.format(setup_type_class=upperfirst(setup_type), setup_type=setup_type),
			],
			body="$this->{setup_type}SetupFactory = ${setup_type}SetupFactory;".format(setup_type=setup_type),
			docstring=[
				'Constructor',
				'',
				'@param \\Magento\\{setup_type_class}\\Setup\\{setup_type_class}SetupFactory ${setup_type}SetupFactory'.format(
					setup_type_class=upperfirst(setup_type),
					setup_type=setup_type
				)
			]
		)) 
		install_data.add_method(Phpmethod('{}'.format(setupType.lower()),
			params=['ModuleDataSetupInterface $setup','ModuleContextInterface $context'],
			docstring=['{@inheritdoc}']))
		if upgrade_data:
			install_data.add_method(Phpmethod('{}'.format(setupType.lower()),
				params=['ModuleDataSetupInterface $setup','ModuleContextInterface $context'],
				body='if (version_compare($context->getVersion(), "' + from_version + '", "<")) {\n\n    ' + methodBody.replace('\n','\n    ') + '\n}\n'))
		else:
			install_data.add_method(Phpmethod('{}'.format(setupType.lower()),
				params=['ModuleDataSetupInterface $setup','ModuleContextInterface $context'],
				body = methodBody))

		etc_module = Xmlnode('config', attributes={
			'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Module/etc/module.xsd"}, nodes=[
			Xmlnode('module', attributes={'name': self.module_name}, nodes=[
				Xmlnode('sequence', attributes={}, nodes=[
					Xmlnode('module', attributes={'name': 'Magento_Sales'})
				])
			])
		])
		self.add_xml('etc/module.xml', etc_module)

		self.add_class(install_data)

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
				 name='sales_entity',
				 choises=cls.SALES_ENTITIES,
				 required=True,
				 default='quote',
				 repeat=True),
			 SnippetParam(
				name='attribute_label', 
				required=True, 
				description='Example: Order Comment',
				regex_validator= r'^[a-zA-Z\d\-_\s]+$',
				error_message='Only alphanumeric',
				repeat=True),
			 SnippetParam(
				 name='frontend_input',
				 choises=cls.FRONTEND_INPUT_TYPE,
				 required=True,  
				 default='text',
				 repeat=True),
			 SnippetParam(
				 name='required',
				 required=True,  
				 default=False,
				 yes_no=True,
				 repeat=True),
			 SnippetParam(
				 name='upgrade_data',
				 default=False,
				 yes_no=True,
				 repeat=True
			 ),
			 SnippetParam(
				 name='from_version',
				 description='1.0.1',
				 default='1.0.1',
				 repeat=True
			 ),
					  ]

	@classmethod
	def extra_params(cls):
		 return [
			SnippetParam(
				name='attribute_code',
				description='Default to lowercase of label',
				regex_validator= r'^[a-zA-Z]{1}\w{0,29}$',
				error_message='Only alphanumeric and underscore characters are allowed, and need to start with a alphabetic character. And can\'t be longer then 30 characters',
				repeat=True),
			 SnippetParam(
				 name='field_size',
				 description='Size of field, Example: 512 for max chars',
				 required=False,
				 regex_validator=r'^\d+$',
				 error_message='Only numeric value allowed.',
				 depend={'frontend_input': r'text|blob|decimal|numeric',},
				 repeat=True
			 ),
			SnippetParam(
				 name='used_in_admin_grid',
				 required=True,  
				 default=False,
				 yes_no=True,
				repeat=True),
			 SnippetParam(
				 name='visible',
				 required=True,
				 default=False,
				 yes_no=True,
				 repeat=True),
		]
