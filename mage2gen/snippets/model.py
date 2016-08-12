# A Magento 2 module generator library
# Copyright (C) 2016 Maikel Martens
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
from collections import OrderedDict
from mage2gen import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam


class ModelSnippet(Snippet):
	description = """
	Model is used to create a easie CRUD interface to the database 

	- **Model ame:** The name of the model, the table name wil be <module_name>_<model_name>.
	- **Field name:** The name of the database table field.
	- **Field type:** The type of database field.
	- **Adminhtml grid:** Add this field to the adminhtml grid layout  

	**Model ID field**:	The snippet will auto add the model id field to the database table, the field name is <model_name>_id.
	"""

	FIELD_TYPE_CHOISES = [
		('boolean','Boolean'),	
		('smallint','Smallint'),	
		('integer','Integer'),
		('bigint', 'Bigint'),
		('float', 'Float'),
		('numeric', 'Numeric'),
		('decimal', 'Decimal'),
		('date', 'Date'),
		('timestamp', 'Timestamp'),
		('datetime', 'Datetime'),
		('text', 'Text'),
		('blob', 'Blob'),
	]

	def add(self, model_name, field_name, field_type='text', adminhtml_grid=False, extra_params=False):
		extra_params = extra_params if extra_params else {}
		
		model_table = '{}_{}'.format(self._module.package.lower(), model_name.lower())
		model_id = '{}_id'.format(model_name.lower())
		
		install_class = Phpclass('Setup\\InstallSchema',implements=['InstallSchemaInterface'],dependencies=[
			'Magento\\Framework\\Setup\\InstallSchemaInterface',
			'Magento\\Framework\\Setup\\ModuleContextInterface',
			'Magento\\Framework\\Setup\\SchemaSetupInterface'])

		# Start setup
		install_method = Phpmethod('install', params=['SchemaSetupInterface $setup','ModuleContextInterface $context'],
			body='$installer = $setup;\n$installer->startSetup();',
			body_return='$setup->endSetup();')
		
		# Create table
		install_method.body.append("$table_{0} = $setup->getConnection()->newTable($setup->getTable('{0}'));".format(model_table))
		
		# add model id field
		install_method.body.append("$table_{table}->addColumn(\n  '{field}',\n  {type},\n  {size},\n  {options},\n  '{comment}'\n);".format(
			table=model_table,
			field=model_id,
			type='\\Magento\\Framework\\DB\\Ddl\\Table::TYPE_INTEGER',
			size='null',
			options="array('identity' => true,'nullable' => false,'primary' => true,'unsigned' => true,)",
			comment='Entity ID'	
		))

		# create options
		options = OrderedDict()
		if extra_params.get('default'):
			options['default'] = "'{}'".format(extra_params.get('default'))
		if not extra_params.get('nullable'):
			options['nullable'] = extra_params.get('nullable')
		if extra_params.get('identity'):
			options['identity'] = True
		if extra_params.get('auto_increment'):
			options['auto_increment'] = True
		if extra_params.get('unsigned'):
			options['unsigned'] = True
		if extra_params.get('precision'):
			options['precision'] = extra_params.get('precision')
		if extra_params.get('scale'):
			options['scale'] = extra_params.get('scale')
		
		options = "[{}]".format(','.join("'{}' => {}".format(key, value) for key, value in options.items()))

		# Add field
		install_method.body.append("$table_{table}->addColumn(\n  '{field}',\n  {type},\n  {size},\n  {options},\n  '{comment}'\n);".format(
			table=model_table,
			field=field_name,
			type='\\Magento\\Framework\\DB\\Ddl\\Table::TYPE_{}'.format(field_type.upper()),
			size=extra_params.get('field_size') or 'null',
			options=options,
			comment=extra_params.get('comment') or field_name	
		))
		
		# End setup + create table 
		install_method.end_body.append('$setup->getConnection()->createTable($table_{});'.format(model_table))

		install_class.add_method(install_method)
		self.add_class(install_class)
		
		# Create resource class
		resource_model_class = Phpclass('Model\\ResourceModel\\' + model_name.replace('_', '\\'), extends='\\Magento\\Framework\\Model\\ResourceModel\\Db\\AbstractDb')
		resource_model_class.add_method(Phpmethod('_construct', access=Phpmethod.PROTECTED, body="$this->_init('{}', '{}');".format(model_table, model_id)))
		self.add_class(resource_model_class)

		# Create model class
		model_class = Phpclass('Model\\' + model_name.replace('_', '\\'), extends='\\Magento\\Framework\\Model\\AbstractModel')
		model_class.add_method(Phpmethod('_construct', access=Phpmethod.PROTECTED, body="$this->_init('{}');".format(resource_model_class.class_namespace)))
		self.add_class(model_class)

		# Create collection
		collection_model_class = Phpclass('Model\\ResourceModel\\' + model_name.replace('_', '\\') + '\\Collection', 
				extends='\\Magento\\Framework\\Model\\ResourceModel\\Db\\Collection\\AbstractCollection')
		collection_model_class.add_method(Phpmethod('_construct', access=Phpmethod.PROTECTED, body="$this->_init(\n  '{}',\n  '{}');".format(
			model_class.class_namespace ,resource_model_class.class_namespace)))
		self.add_class(collection_model_class)

		# add grid 
		if adminhtml_grid:
			frontname = self.module_name.lower()
			data_source_id = '{}_grid_data_source'.format(model_table)
			
			# create controller
			index_controller_class = Phpclass('Controller\\Adminhtml\\' + model_name.replace('_', '\\') + '\\Index', extends='\\Magento\\Framework\\App\\Action\\Action',
					attributes=['protected $resultPageFactory;'])
			
			index_controller_class.add_method(Phpmethod('__construct', 
				params=['\\Magento\\Framework\\App\\Action\\Context $context', '\\Magento\\Framework\\View\\Result\\PageFactory $resultPageFactory'],
				body='$this->resultPageFactory = $resultPageFactory;\nparent::__construct($context);'))
			
			index_controller_class.add_method(Phpmethod('execute', body_return='return $this->resultPageFactory->create();'))
			
			self.add_class(index_controller_class)

			# create menu.xml
			self.add_xml('etc/adminhtml/menu.xml', Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:module:Magento_Backend:etc/menu.xsd"}, nodes=[
				Xmlnode('menu', nodes=[
					Xmlnode('add', attributes={
						'id': "{}::top_level".format(self.module_name),
						'title': self._module.package,
						'module': self.module_name,
						'sortOrder': 9999,
						'resource': 'Magento_Backend::content',
					}),
					Xmlnode('add', attributes={
						'id': "{}::{}".format(self.module_name, model_table),
						'title': model_name.replace('_', ' '),
						'module': self.module_name,
						'sortOrder': 9999,
						'resource': 'Magento_Backend::content',
						'parent': '{}::top_level'.format(self.module_name),
						'action': '{}/{}/index'.format(frontname, model_name.lower().replace('_', '\\'))
					})
				])	
			]))

			# Create routes.xml
			self.add_xml('etc/adminhtml/routes.xml', Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation': 'urn:magento:framework:App/etc/routes.xsd'}, nodes=[
				Xmlnode('router', attributes={'id': 'admin'}, nodes=[
					Xmlnode('route', attributes={'frontName': frontname, 'id':frontname}, nodes=[
						Xmlnode('module', attributes={'before': 'Magento_Backend', 'name': self.module_name})
					])	
				])	
			]))

			# di.xml
			self.add_xml('etc/di.xml', Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:framework:ObjectManager/etc/config.xsd"}, nodes=[
				Xmlnode('virtualType', attributes={
					'name': collection_model_class.class_namespace.replace('Collection', 'Grid\\Collection'),
					'type': 'Magento\\Framework\\View\\Element\\UiComponent\\DataProvider\\SearchResult',
					}, nodes=[
					Xmlnode('arguments', nodes=[
						Xmlnode('argument', attributes={'name': 'mainTable', 'xsi:type': 'string'}, node_text=model_table),
						Xmlnode('argument', attributes={'name': 'resourceModel', 'xsi:type': 'string'}, node_text= collection_model_class.class_namespace),
					])	
				]),
				Xmlnode('type', attributes={'name': 'Magento\\Framework\\View\\Element\\UiComponent\\DataProvider\\CollectionFactory'}, nodes=[
					Xmlnode('arguments', nodes=[
						Xmlnode('argument', attributes={'name': 'collections', 'xsi:type': 'array'}, nodes=[
							Xmlnode('item', attributes={'name': data_source_id, 'xsi:type': 'string'}, node_text=collection_model_class.class_namespace.replace('Collection', 'Grid\\Collection'))	
						])	
					])	
				])
			]))

			# create layout.xml
			self.add_xml('view/adminhtml/layout/{}_{}_index.xml'.format(frontname, model_name.lower()), 
				Xmlnode('page', attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:framework:View/Layout/etc/page_configuration.xsd"}, nodes=[
					Xmlnode('update', attributes={'handle': 'styles'}),
					Xmlnode('body', nodes=[
						Xmlnode('referenceContainer', attributes={'name': 'content'}, nodes=[
							Xmlnode('uiComponent', attributes={'name': '{}_index'.format(model_table)})	
						])
					])
				]))

			# create components.xml
			data_source_xml = Xmlnode('dataSource', attributes={'name': data_source_id}, nodes=[
				Xmlnode('argument', attributes={'name': 'dataProvider', 'xsi:type': 'configurableObject'}, nodes=[
					Xmlnode('argument', attributes={'name': 'class', 'xsi:type': 'string'}, node_text='Magento\\Framework\\View\\Element\\UiComponent\\DataProvider\\DataProvider'),
					Xmlnode('argument', attributes={'name': 'name', 'xsi:type': 'string'}, node_text= data_source_id),
					Xmlnode('argument', attributes={'name': 'primaryFieldName', 'xsi:type': 'string'}, node_text=model_id),
					Xmlnode('argument', attributes={'name': 'requestFieldName', 'xsi:type': 'string'}, node_text='id'),
					Xmlnode('argument', attributes={'name': 'data', 'xsi:type': 'array'}, nodes=[
						Xmlnode('item', attributes={'name': 'config', 'xsi:type': 'array'}, nodes=[
							Xmlnode('item', attributes={'name': 'component', 'xsi:type': 'string'}, node_text='Magento_Ui/js/grid/provider'),
							Xmlnode('item', attributes={'name': 'update_url', 'xsi:type': 'url', 'path': 'mui/index/render'}),
							Xmlnode('item', attributes={'name': 'storageConfig', 'xsi:type': 'array'}, nodes=[
								Xmlnode('item', attributes={'name': 'indexField', 'xsi:type': 'string'}, node_text=model_id)	
							]),
						])	
					]),
				])
			])

			columns_xml = Xmlnode('columns', attributes={'name': '{}_columns'.format(model_table)}, nodes=[
				Xmlnode('selectionsColumn', attributes={'name': 'ids'}, nodes=[
					Xmlnode('argument', attributes={'name': 'data', 'xsi:type': 'array'}, nodes=[
						Xmlnode('item', attributes={'name': 'config', 'xsi:type': 'array'}, nodes=[
							Xmlnode('item', attributes={'name': 'indexField', 'xsi:type': 'string'}, node_text=model_id)	
						])
					])		
				]),
				Xmlnode('column', attributes={'name': model_id}, nodes=[
					Xmlnode('argument', attributes={'name': 'data', 'xsi:type': 'array'}, nodes=[
						Xmlnode('item', attributes={'name': 'config', 'xsi:type': 'array'}, nodes=[
							Xmlnode('item', attributes={'name': 'filter', 'xsi:type': 'string'}, node_text='text'),	
							Xmlnode('item', attributes={'name': 'sorting', 'xsi:type': 'string'}, node_text='asc'),	
							Xmlnode('item', attributes={'name': 'label', 'xsi:type': 'string', 'translate': 'true'}, node_text='ID'),	
						])
					])		
				]),
				Xmlnode('column', attributes={'name': field_name}, nodes=[
					Xmlnode('argument', attributes={'name': 'data', 'xsi:type': 'array'}, nodes=[
						Xmlnode('item', attributes={'name': 'config', 'xsi:type': 'array'}, nodes=[
							Xmlnode('item', attributes={'name': 'filter', 'xsi:type': 'string'}, node_text='text'),	
							Xmlnode('item', attributes={'name': 'sorting', 'xsi:type': 'string'}, node_text='asc'),	
							Xmlnode('item', attributes={'name': 'label', 'xsi:type': 'string', 'translate': 'true'}, node_text=field_name),	
						])
					])		
				]),
			])

			self.add_xml('view/adminhtml/ui_component/{}_index.xml'.format(model_table), 
				Xmlnode('listing', attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:module:Magento_Ui:etc/ui_configuration.xsd"}, nodes=[
					Xmlnode('argument', attributes={'name': 'context', 'xsi:type': 'configurableObject'}, nodes=[
						Xmlnode('argument', attributes={'name': 'class', 'xsi:type': 'string'}, node_text='Magento\\Framework\\View\\Element\\UiComponent\\Context'),
						Xmlnode('argument', attributes={'name': 'namespace', 'xsi:type': 'string'}, node_text='{}_index'.format(model_table)),
					]),
					Xmlnode('argument', attributes={'name': 'data', 'xsi:type': 'array'}, nodes=[
						Xmlnode('item', attributes={'name': 'js_config', 'xsi:type': 'array'}, nodes=[
							Xmlnode('item', attributes={'name': 'provider', 'xsi:type': 'string'}, node_text='{}_index.{}'.format(model_table, data_source_id)),	
							Xmlnode('item', attributes={'name': 'deps', 'xsi:type': 'string'}, node_text='{}_index.{}'.format(model_table, data_source_id)),	
						]),
						Xmlnode('item', attributes={'name': 'spinner', 'xsi:type': 'string'}, node_text='{}_columns'.format(model_table)),
					]),
					data_source_xml,
					columns_xml,
				]))

	@classmethod
	def params(cls):
		return [
			SnippetParam(
				name='model_name', 
				required=True, 
				regex_validator= r'^[a-zA-Z]{1}\w+$',
				error_message='Only alphanumeric and underscore characters are allowed, and need to start with a alphabetic character.'
			),
			SnippetParam(
				name='field_name', 
				required=True, 
				regex_validator= r'^[a-zA-Z]{1}\w+$',
				error_message='Only alphanumeric and underscore characters are allowed, and need to start with a alphabetic character.'
			),
			SnippetParam(
				name='field_type', 
				choises=cls.FIELD_TYPE_CHOISES, 
				default='text',
			),
			SnippetParam(name='adminhtml_grid', yes_no=True),
		]

	@classmethod
	def extra_params(cls):
		return [
			SnippetParam('comment', required=False),
			SnippetParam('default', required=False),
			SnippetParam('nullable', yes_no=True, default=True),
			SnippetParam('identity', yes_no=True),
			SnippetParam('auto_increment', yes_no=True),
			'Extra',
			SnippetParam(
				name='field_size', 
				required=False, 
				regex_validator= r'^\d+$',
				error_message='Only numeric value allowed.',
				depend={'field_type': r'text|blob|decimal|numeric'}
			),
			SnippetParam(
				name='precision', 
				required=False, 
				regex_validator= r'^\d+$',
				error_message='Only numeric value allowed.',
				depend={'field_type': r'decimal|numeric'}
			),
			SnippetParam(
				name='scale', 
				required=False, 
				regex_validator= r'^\d+$',
				error_message='Only numeric value allowed.',
				depend={'field_type': r'decimal|numeric'}
			),
			SnippetParam(
				name='unsigned', 
				yes_no=True, 
				depend={'field_type': r'smallint|integer|bigint|float|decimal|numeric'}
			),


		]


