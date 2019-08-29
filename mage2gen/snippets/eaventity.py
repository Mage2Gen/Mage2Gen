# A Magento 2 module generator library
# Copyright (C) 2019 Lewis Voncken | Mr. Lewis
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
from .. import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam
from ..utils import upperfirst, lowerfirst
from ..module import TEMPLATE_DIR

# Long boring code to add a lot of PHP classes and xml, only go here if you feel like too bring you happiness down. 
# Or make your day happy that you don't maintain this code :)

class InterfaceClass(Phpclass):

	template_file = os.path.join(TEMPLATE_DIR,'interface.tmpl')

class InterfaceMethod(Phpmethod):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.template_file = os.path.join(TEMPLATE_DIR,'interfacemethod.tmpl')

class EavEntitySnippet(Snippet):
	snippet_label = 'EAV Entity'
	description = """
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.count = 0

	def add(self, entity_name, adminhtml_grid=False, adminhtml_form=False,web_api=False, extra_params=False):
		field_name = 'title'
		field_type = 'varchar'

		self.count += 1
		extra_params = extra_params if extra_params else {}

		entity_table = '{}_{}_entity'.format(self._module.package.lower(), entity_name.lower())
		entity_id = 'entity_id'.format(entity_name.lower())

		field_element_type = 'input'

		split_field_name = field_name.split('_')
		field_name_capitalized = ''.join(upperfirst(item) for item in split_field_name)

		split_entity_name = entity_name.split('_')
		entity_name_capitalized = ''.join(upperfirst(item) for item in split_entity_name)
		entity_name_capitalized_after = entity_name_capitalized[0].lower() + entity_name_capitalized[1:]

		split_entity_id = entity_id.split('_')
		entity_id_capitalized = ''.join(upperfirst(item) for item in split_entity_id)
		entity_id_capitalized_after = entity_id_capitalized[0].lower() + entity_id_capitalized[1:]

		collection_entity_class_name = "\\{}\\{}\\Model\\ResourceModel\\{}\\Collection".format(self._module.package,
			self._module.name,
		  	entity_name_capitalized.replace('_', '\\'),
		)

		extension_interface_class_name = "\\{}\\{}\\Api\\Data\\{}ExtensionInterface".format(self._module.package,
		  	self._module.name,
		  	entity_name_capitalized.replace('_', '\\')
		)

		top_level_menu = extra_params.get('top_level_menu', True)

		# create options
		required = False
		attributes = {
			'xsi:type': "{}".format(field_type),
			'name': "{}".format(field_name),
			'nullable': "true"
		}
		if extra_params.get('unsigned'):
			attributes['unsigned'] = 'true'
			attributes['length'] = '255'

		for eav_type in ['datetime', 'decimal', 'int', 'text', 'varchar']:
			eav_entity_type_table = "{}_{}".format(entity_table, eav_type)
			eav_entity_type_table_upper = eav_entity_type_table.upper()
			additionalIndex = []
			if eav_type != 'text':
				additionalIndex += Xmlnode('index', attributes={
							'referenceId': "{}_ENTITY_ID_ATTRIBUTE_ID_VALUE".format(eav_entity_type_table_upper),
							'indexType': "btree"
						}, match_attributes=["referenceId"], nodes=[
							Xmlnode('column', attributes={
								'name': "entity_id",
							}),
							Xmlnode('column', attributes={
								'name': "attribute_id",
							}),
							Xmlnode('column', attributes={
								'name': "value",
							})
						]),
			self.add_xml('etc/db_schema.xml', Xmlnode('schema', nodes=[
				Xmlnode('table', attributes={
					'name': "{}_{}".format(entity_table, eav_type),
					'resource': "default",
					'engine': "innodb",
					'comment': "{} Table".format(eav_entity_type_table)
				},  nodes=[

					Xmlnode('column', attributes={
						'xsi:type': "int",
						'name': "value_id",
						'padding': "11",
						'unsigned': "false",
						'nullable': "false",
						'identity': "true",
						'comment': "Value ID",
					}),
					Xmlnode('column', attributes={
						'xsi:type': "smallint",
						'name': "attribute_id",
						'padding': "5",
						'unsigned': "true",
						'nullable': "false",
						'identity': "false",
						'default': "0",
						'comment': "Attribute ID",
					}),
					Xmlnode('column', attributes={
						'xsi:type': "int",
						'name': "entity_id",
						'padding': "10",
						'unsigned': "true",
						'nullable': "false",
						'identity': "false",
						'default': "0",
						'comment': "Entity ID",
					}),
					Xmlnode('constraint', attributes={
						'xsi:type': "primary",
						'referenceId': "PRIMARY".format(entity_id)
					}, match_attributes=["referenceId"], nodes=[
						Xmlnode('column', attributes={
							'name': "value_id"
						})
					]),
					Xmlnode('constraint', attributes={
						'xsi:type': "foreign",
						'referenceId': "{}_ATTRIBUTE_ID_EAV_ATTRIBUTE_ATTRIBUTE_ID".format(eav_entity_type_table_upper),
						'table': eav_entity_type_table,
						'column': "attribute_id",
						'referenceTable': "eav_attribute",
						'referenceColumn': "attribute_id",
						'onDelete': "CASCADE",
					},match_attributes=["referenceId"]),
					Xmlnode('constraint', attributes={
						'xsi:type': "foreign",
						'referenceId': "{}_ENTITY_ID_{}_ENTITY_ID".format(eav_entity_type_table_upper, entity_table.upper()),
						'table': eav_entity_type_table,
						'column': "entity_id",
						'referenceTable': entity_table,
						'referenceColumn': entity_id,
						'onDelete': "CASCADE",
					}, match_attributes=["referenceId"]),
					Xmlnode('constraint', attributes={
						'xsi:type': "unique",
						'referenceId': "{}_ENTITY_ID_ATTRIBUTE_ID".format(eav_entity_type_table_upper)
					}, match_attributes=["referenceId"], nodes=[
						Xmlnode('column', attributes={
							'name': "entity_id",
						}),
						Xmlnode('column', attributes={
							'name': "attribute_id",
						})
					]),
					Xmlnode('index', attributes={
						'referenceId': "{}_ATTRIBUTE_ID".format(eav_entity_type_table_upper),
						'indexType': "btree"
					}, match_attributes=["referenceId"], nodes=[
						Xmlnode('column', attributes={
							'name': "attribute_id",
						})
					]),
					] +
					additionalIndex
				)
			]))



		# update db_schema.xml preferences
		self.add_xml('etc/db_schema.xml', Xmlnode('schema', attributes={
			'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Setup/Declaration/Schema/etc/schema.xsd"}, nodes=[
			Xmlnode('table', attributes={
				'name': "{}".format(entity_table),
				'resource': "default",
				'engine': "innodb",
				'comment': "{} Table".format(entity_table)
			}, match_attributes=["name"], nodes=[
				Xmlnode('column', attributes={
					'xsi:type': "{}".format('int'),
					'name': entity_id,
					'padding': "{}".format('10'),
					'unsigned': "{}".format('true'),
					'nullable': "{}".format('false'),
					'identity': "{}".format('true'),
					'comment': "{}".format('Entity Id')
				}),
				Xmlnode('constraint', attributes={
					'xsi:type': "primary",
					'referenceId': "PRIMARY".format(entity_id)
				}, match_attributes=["referenceId"], nodes=[
					Xmlnode('column', attributes={
						'name': entity_id
					})
				]),
				Xmlnode('column', attributes=attributes)
			]),
			Xmlnode('table', attributes={
				'name': "{}_datetime".format(entity_table),
				'resource': "default",
				'engine': "innodb",
				'comment': "{} Datetime Table".format(entity_table)
			}, match_attributes=["name"], nodes=
				[
					Xmlnode('column', attributes={
						'xsi:type': "datetime",
						'name': "value",
						'on_update': "false",
						'nullable': "false",
						'comment': "Value",
					})
				]
			),
			Xmlnode('table', attributes={
				'name': "{}_decimal".format(entity_table),
			}, match_attributes=["name"], nodes=
				[
					Xmlnode('column', attributes={
						'xsi:type': "decimal",
						'name': "value",
						'scale': "4",
						'precision': "12",
						'unsigned': "false",
						'nullable': "false",
						'default': "0",
						'comment': "Value",
					})
				]
			),
			Xmlnode('table', attributes={
				'name': "{}_int".format(entity_table),
			}, match_attributes=["name"], nodes=
					[
						Xmlnode('column', attributes={
							'xsi:type': "int",
							'name': "value",
							'padding': "11",
							'unsigned': "false",
							'nullable': "false",
							'identity': "false",
							'default': "0",
							'comment': "Value",
						})
					]
			),
			Xmlnode('table', attributes={
				'name': "{}_text".format(entity_table),
			}, match_attributes=["name"], nodes=
					[
						Xmlnode('column', attributes={
							'xsi:type': "text",
							'name': "value",
							'nullable': "true",
							'comment': "Value",
						})
					]
			),
			Xmlnode('table', attributes={
				'name': "{}_varchar".format(entity_table),
			}, match_attributes=["name"], nodes=
					[
						Xmlnode('column', attributes={
							'xsi:type': "varchar",
							'name': "value",
							'nullable': "true",
							'length': "255",
							'comment': "Value",
						})
					]
			),
		]))

		# Create resource class
		resource_entity_class = Phpclass('Model\\ResourceModel\\' + entity_name_capitalized.replace('_', '\\'), extends='\\Magento\\Eav\\Model\\Entity\\AbstractEntity')
		resource_entity_class.add_method(Phpmethod('_construct',
			access=Phpmethod.PROTECTED,
			body="$this->setType('{}');".format(entity_table),
			docstring=[
				'Define resource model',
				'',
				'@return void',
				]))
		self.add_class(resource_entity_class)

		# Create api data interface class
		api_data_class =  InterfaceClass('Api\\Data\\' + entity_name_capitalized.replace('_', '\\') + 'Interface',
			extends='\\Magento\\Framework\\Api\\ExtensibleDataInterface',
			attributes=[
				"const {} = '{}';".format(field_name.upper(),field_name),"const {} = '{}';".format(entity_id.upper(),entity_id)
			])

		api_data_class.add_method(InterfaceMethod('get'+entity_id_capitalized,docstring=['Get {}'.format(entity_id),'@return {}'.format('string|null')]))
		self.add_class(api_data_class)

		api_data_class.add_method(InterfaceMethod('set'+entity_id_capitalized,params=['${}'.format(entity_id_capitalized_after)],docstring=['Set {}'.format(entity_id),'@param string ${}'.format(entity_id_capitalized_after),'@return \{}'.format(api_data_class.class_namespace)]))
		self.add_class(api_data_class)

		api_data_class.add_method(InterfaceMethod('get'+field_name_capitalized,docstring=['Get {}'.format(field_name),'@return {}'.format('string|null')]))
		self.add_class(api_data_class)

		api_data_class.add_method(InterfaceMethod('set'+field_name_capitalized,params=['${}'.format(lowerfirst(field_name_capitalized))],docstring=['Set {}'.format(field_name),'@param string ${}'.format(lowerfirst(field_name_capitalized)),'@return \{}'.format(api_data_class.class_namespace)]))
		self.add_class(api_data_class)

		api_data_class.add_method(InterfaceMethod('getExtensionAttributes', docstring=['Retrieve existing extension attributes object or create a new one.','@return ' + extension_interface_class_name + '|null']))
		api_data_class.add_method(InterfaceMethod('setExtensionAttributes', params=[extension_interface_class_name + ' $extensionAttributes'], docstring=['Set an extension attributes object.','@param ' + extension_interface_class_name +' $extensionAttributes','@return $this']))
		self.add_class(api_data_class)


		# Create api data interface class
		api_data_search_class =  InterfaceClass('Api\\Data\\' + entity_name_capitalized.replace('_', '\\') + 'SearchResultsInterface',extends='\Magento\Framework\Api\SearchResultsInterface')
		api_data_search_class.add_method(InterfaceMethod('getItems',docstring=['Get {} list.'.format(entity_name),'@return \{}[]'.format(api_data_class.class_namespace)]))
		api_data_search_class.add_method(InterfaceMethod('setItems',params=['array $items'],docstring=['Set {} list.'.format(field_name),'@param \{}[] $items'.format(api_data_class.class_namespace),'@return $this']))
		self.add_class(api_data_search_class)

		# Create api data interface class
		api_repository_class =  InterfaceClass('Api\\' + entity_name_capitalized.replace('_', '\\') + 'RepositoryInterface',dependencies=['Magento\Framework\Api\SearchCriteriaInterface'])
		api_repository_class.add_method(InterfaceMethod('save',params=['\{} ${}'.format(api_data_class.class_namespace,entity_name_capitalized_after)],docstring=['Save {}'.format(entity_name),'@param \{} ${}'.format(api_data_class.class_namespace,entity_name_capitalized_after),'@return \{}'.format(api_data_class.class_namespace),'@throws \Magento\Framework\Exception\LocalizedException']))
		api_repository_class.add_method(InterfaceMethod('getById',params=['${}'.format(entity_id_capitalized_after)],docstring=['Retrieve {}'.format(entity_name),'@param string ${}'.format(entity_id_capitalized_after),'@return \{}'.format(api_data_class.class_namespace),'@throws \Magento\Framework\Exception\LocalizedException']))
		api_repository_class.add_method(InterfaceMethod('getList',params= ['\Magento\Framework\Api\SearchCriteriaInterface $searchCriteria'], docstring=['Retrieve {} matching the specified criteria.'.format(entity_name),'@param \Magento\Framework\Api\SearchCriteriaInterface $searchCriteria','@return \{}'.format(api_data_search_class.class_namespace),'@throws \Magento\Framework\Exception\LocalizedException']))
		api_repository_class.add_method(InterfaceMethod('delete',params=['\{} ${}'.format(api_data_class.class_namespace,entity_name_capitalized_after)],docstring=['Delete {}'.format(entity_name),'@param \{} ${}'.format(api_data_class.class_namespace,entity_name_capitalized_after),'@return bool true on success','@throws \Magento\Framework\Exception\LocalizedException']))
		api_repository_class.add_method(InterfaceMethod('deleteById',params=['${}'.format(entity_id_capitalized_after)],docstring=['Delete {} by ID'.format(entity_name),'@param string ${}'.format(entity_id_capitalized_after),'@return bool true on success','@throws \\Magento\\Framework\\Exception\\NoSuchEntityException','@throws \\Magento\\Framework\\Exception\\LocalizedException']))
		self.add_class(api_repository_class)

		# Create model class
		entity_class = Phpclass('Model\\' + entity_name_capitalized.replace('_', '\\'),
			dependencies=[
				api_data_class.class_namespace,
				api_data_class.class_namespace + 'Factory',
				'Magento\\Framework\\Api\\DataObjectHelper',
			],
			extends='\\Magento\\Framework\\Model\\AbstractModel',
			attributes=[
				"const ENTITY = '{}';".format(entity_table),
				'protected ${}DataFactory;\n'.format(entity_name.lower()),
				'protected $dataObjectHelper;\n',
				'protected $_eventPrefix = \'{}\';'.format(entity_table),
			])
		entity_class.add_method(Phpmethod('__construct', access=Phpmethod.PUBLIC,
			params=[
				"\Magento\Framework\Model\Context $context",
				"\Magento\Framework\Registry $registry",
				"{}InterfaceFactory ${}DataFactory".format(entity_name_capitalized, entity_name.lower()),
				"DataObjectHelper $dataObjectHelper",
				"\\" + resource_entity_class.class_namespace + " $resource",
				collection_entity_class_name + " $resourceCollection",
				"array $data = []",
			],
			body="""$this->{variable}DataFactory = ${variable}DataFactory;
			$this->dataObjectHelper = $dataObjectHelper;
			parent::__construct($context, $registry, $resource, $resourceCollection, $data);
			""".format(variable=entity_name.lower()),
			docstring=[
				"@param \Magento\Framework\Model\Context $context",
				"@param \Magento\Framework\Registry $registry",
				"@param {}InterfaceFactory ${}DataFactory".format(entity_name_capitalized, entity_name.lower()),
				"@param DataObjectHelper $dataObjectHelper",
				"@param \\" + resource_entity_class.class_namespace + " $resource",
				"@param " + collection_entity_class_name + " $resourceCollection",
				"@param array $data",
			]
		))
		entity_class.add_method(Phpmethod('getDataModel', access=Phpmethod.PUBLIC,
			body="""${variable}Data = $this->getData();
			
			${variable}DataObject = $this->{variable}DataFactory->create();
			$this->dataObjectHelper->populateWithArray(
			    ${variable}DataObject,
			    ${variable}Data,
			    {variable_upper}Interface::class
			);
			
			return ${variable}DataObject;
			""".format(variable=entity_name.lower(), variable_upper=entity_name_capitalized),
			docstring=[
				"Retrieve {} model with {} data".format(entity_name.lower(), entity_name.lower()),
				"@return {}Interface".format(entity_name_capitalized),
			]
		))
		self.add_class(entity_class)

		entity_setup = Phpclass('Setup\\{}Setup'.format(entity_name_capitalized.replace('_', '\\')),
								extends='EavSetup',
								dependencies=[
									'Magento\\Eav\\Setup\\EavSetup'
								]
								)

		entity_setup.add_method(
			Phpmethod('getDefaultEntities', body="""
							return [\r
							     \{entity_class}::ENTITY => [
							        'entity_model' => \{resource_class}::class,
							        'table' => '{entity_table}',
							        'attributes' => [
							        	'title' => [
							        		'type' => 'static'
							        	]
							    	]
							    ]
							];""".format(entity_class=entity_class.class_namespace, entity_table=entity_table, resource_class=resource_entity_class.class_namespace))
		)

		self.add_class(entity_setup)

		install_patch = Phpclass(
			'Setup\\Patch\\Data\\Default{}Entity'.format(entity_name_capitalized.replace('_', '\\')),
			implements=['DataPatchInterface'],
			dependencies=[
				'Magento\\Framework\\Setup\\Patch\\DataPatchInterface',
				'Magento\\Framework\\Setup\\ModuleDataSetupInterface',
				"{}Factory".format(entity_setup.class_namespace),
				entity_setup.class_namespace
			],
			attributes=[
				"/**\n\t * @var ModuleDataSetupInterface\n\t */\n\tprivate $moduleDataSetup;",
				"/**\n\t * @var {}Setup\n\t */\n\tprivate ${}SetupFactory;".format(entity_name_capitalized.replace('_', '\\'), lowerfirst(entity_name_capitalized.replace('_', '\\')))
			]
			)

		install_patch.add_method(Phpmethod(
			'__construct',
			params=[
				'ModuleDataSetupInterface $moduleDataSetup',
				'{}SetupFactory ${}SetupFactory'.format(entity_name_capitalized.replace('_', '\\'), lowerfirst(entity_name_capitalized.replace('_', '\\')))
			],
			body="$this->moduleDataSetup = $moduleDataSetup;\n$this->{variable}SetupFactory = ${variable}SetupFactory;".format(variable=lowerfirst(entity_name_capitalized.replace('_', '\\'))),
			docstring=[
				'Constructor',
				'',
				'@param ModuleDataSetupInterface $moduleDataSetup',
				'@param {}SetupFactory ${}SetupFactory'.format(entity_name_capitalized.replace('_', '\\'), lowerfirst(entity_name_capitalized.replace('_', '\\')))
			]
		))

		install_patch.add_method(Phpmethod('apply',
										   body_start='$this->moduleDataSetup->getConnection()->startSetup();',
										   body_return='$this->moduleDataSetup->getConnection()->endSetup();',
										   body="""
					/** @var {class_name}Setup $customerSetup */
					${variable}Setup = $this->{variable}SetupFactory->create(['setup' => $this->moduleDataSetup]);
					${variable}Setup->installEntities();
					""".format(variable=lowerfirst(entity_name_capitalized.replace('_', '\\')), class_name=entity_name_capitalized.replace('_', '\\')),
										   docstring=['{@inheritdoc}']))
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



		etc_module = Xmlnode('config', attributes={
			'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Module/etc/module.xsd"}, nodes=[
			Xmlnode('module', attributes={'name': self.module_name}, nodes=[
				Xmlnode('sequence', attributes={}, nodes=[
				Xmlnode('module', attributes={'name': 'Magento_Eav'})
			])
			])
		])
		self.add_xml('etc/module.xml', etc_module)
		
		# Create collection
		collection_entity_class = Phpclass('Model\\ResourceModel\\' + entity_name_capitalized.replace('_', '\\') + '\\Collection',
				extends='\\Magento\\Eav\\Model\\Entity\\Collection\\AbstractCollection')
		collection_entity_class.add_method(Phpmethod('_construct',
			access=Phpmethod.PROTECTED,
			body="$this->_init(\n    \{}::class,\n    \{}::class\n);".format(
				entity_class.class_namespace ,resource_entity_class.class_namespace),
			docstring=[
				'Define resource model',
				'',
				'@return void',
				]))
		self.add_class(collection_entity_class)

		# Create Repository Class
		entity_repository_class = Phpclass('Model\\' + entity_name_capitalized.replace('_', '\\') + 'Repository',
			dependencies=[
				api_repository_class.class_namespace,
				api_data_search_class.class_namespace + 'Factory',
				api_data_class.class_namespace + 'Factory',
				'Magento\\Framework\\Api\\DataObjectHelper',
				'Magento\\Framework\\Exception\\CouldNotDeleteException',
				'Magento\\Framework\\Exception\\NoSuchEntityException',
				'Magento\\Framework\\Exception\\CouldNotSaveException',
				'Magento\\Framework\\Reflection\\DataObjectProcessor',
				'Magento\\Framework\\Api\\SearchCriteria\\CollectionProcessorInterface',
				resource_entity_class.class_namespace + ' as Resource' + entity_name_capitalized,
				collection_entity_class.class_namespace + 'Factory as '+ entity_name_capitalized +'CollectionFactory',
				'Magento\\Store\\Model\\StoreManagerInterface',
				'Magento\\Framework\\Api\\ExtensionAttribute\\JoinProcessorInterface',
				'Magento\\Framework\\Api\\ExtensibleDataObjectConverter'
			],
			attributes=[
				'protected $resource;\n',
				'protected ${}Factory;\n'.format(entity_name_capitalized_after),
				'protected ${}CollectionFactory;\n'.format(entity_name_capitalized_after),
    			'protected $searchResultsFactory;\n',
    			'protected $dataObjectHelper;\n',
    			'protected $dataObjectProcessor;\n',
    			'protected $data{}Factory;\n'.format(entity_name_capitalized),
				'protected $extensionAttributesJoinProcessor;\n',
    			'private $storeManager;\n',
				'private $collectionProcessor;\n',
				'protected $extensibleDataObjectConverter;'
			],
			implements=[entity_name_capitalized.replace('_', '\\') + 'RepositoryInterface']
		)
		entity_repository_class.add_method(Phpmethod('__construct', access=Phpmethod.PUBLIC,
			params=[
				"Resource{} $resource".format(entity_name_capitalized),
		        "{}Factory ${}Factory".format(entity_name_capitalized,entity_name_capitalized_after),
		        "{}InterfaceFactory $data{}Factory".format(entity_name_capitalized,entity_name_capitalized),
		        "{}CollectionFactory ${}CollectionFactory".format(entity_name_capitalized,entity_name_capitalized_after),
		        "{}SearchResultsInterfaceFactory $searchResultsFactory".format(entity_name_capitalized),
		        "DataObjectHelper $dataObjectHelper",
		        "DataObjectProcessor $dataObjectProcessor",
		        "StoreManagerInterface $storeManager",
		        "CollectionProcessorInterface $collectionProcessor",
				"JoinProcessorInterface $extensionAttributesJoinProcessor",
				"ExtensibleDataObjectConverter $extensibleDataObjectConverter"
			],
			body="""$this->resource = $resource;
			$this->{variable}Factory = ${variable}Factory;
			$this->{variable}CollectionFactory = ${variable}CollectionFactory;
			$this->searchResultsFactory = $searchResultsFactory;
			$this->dataObjectHelper = $dataObjectHelper;
			$this->data{variable_upper}Factory = $data{variable_upper}Factory;
			$this->dataObjectProcessor = $dataObjectProcessor;
			$this->storeManager = $storeManager;
			$this->collectionProcessor = $collectionProcessor;
			$this->extensionAttributesJoinProcessor = $extensionAttributesJoinProcessor;
			$this->extensibleDataObjectConverter = $extensibleDataObjectConverter;
			""".format(variable=entity_name_capitalized_after,variable_upper=entity_name_capitalized),
			docstring=[
				"@param Resource{} $resource".format(entity_name_capitalized),
				"@param {}Factory ${}Factory".format(entity_name_capitalized,entity_name_capitalized_after),
				"@param {}InterfaceFactory $data{}Factory".format(entity_name_capitalized,entity_name_capitalized),
				"@param {}CollectionFactory ${}CollectionFactory".format(entity_name_capitalized,entity_name_capitalized_after),
				"@param {}SearchResultsInterfaceFactory $searchResultsFactory".format(entity_name_capitalized),
				"@param DataObjectHelper $dataObjectHelper",
				"@param DataObjectProcessor $dataObjectProcessor",
				"@param StoreManagerInterface $storeManager",
				"@param CollectionProcessorInterface $collectionProcessor",
				"@param JoinProcessorInterface $extensionAttributesJoinProcessor",
				"@param ExtensibleDataObjectConverter $extensibleDataObjectConverter",
			]
		))
		entity_repository_class.add_method(Phpmethod('save', access=Phpmethod.PUBLIC,
			params=['\\' + api_data_class.class_namespace + ' $' + entity_name_capitalized_after],
			body="""/* if (empty(${variable}->getStoreId())) {{
					    $storeId = $this->storeManager->getStore()->getId();
					    ${variable}->setStoreId($storeId);
					}} */
					
					${variable}Data = $this->extensibleDataObjectConverter->toNestedArray(
					    ${variable},
					    [],
					    \{data_interface}::class
					);
					
					${variable}Model = $this->{variable}Factory->create()->setData(${variable}Data);
					
					try {{
					    $this->resource->save(${variable}Model);
					}} catch (\Exception $exception) {{
					    throw new CouldNotSaveException(__(
					        'Could not save the {variable}: %1',
					        $exception->getMessage()
					    ));
					}}
					return ${variable}Model->getDataModel();
			""".format(data_interface=api_data_class.class_namespace, variable=entity_name_capitalized_after),
			docstring=['{@inheritdoc}']
		))
		entity_repository_class.add_method(Phpmethod('getById', access=Phpmethod.PUBLIC,
			params=['${}Id'.format(entity_name_capitalized_after)],
			body="""${variable} = $this->{variable}Factory->create();
			$this->resource->load(${variable}, ${variable}Id);
			if (!${variable}->getId()) {{
			    throw new NoSuchEntityException(__('{entity_name} with id "%1" does not exist.', ${variable}Id));
			}}
			return ${variable}->getDataModel();
			""".format(variable=entity_name_capitalized_after,entity_name=entity_name),
			docstring=['{@inheritdoc}']
		))
		entity_repository_class.add_method(Phpmethod('getList', access=Phpmethod.PUBLIC,
			params=['\Magento\Framework\Api\SearchCriteriaInterface $criteria'],
			body="""$collection = $this->{variable}CollectionFactory->create();
			
					$this->extensionAttributesJoinProcessor->process(
					    $collection,
					    \{data_interface}::class
					);
			
					$this->collectionProcessor->process($criteria, $collection);
					
					$searchResults = $this->searchResultsFactory->create();
					$searchResults->setSearchCriteria($criteria);
					
					$items = [];
					foreach ($collection as $model) {{
					    $items[] = $model->getDataModel();
					}}
					
					$searchResults->setItems($items);
					$searchResults->setTotalCount($collection->getSize());
					return $searchResults;
			""".format(variable=entity_name_capitalized_after,data_interface=api_data_class.class_namespace,variable_upper=entity_name_capitalized),
			docstring=['{@inheritdoc}']
		))
		entity_repository_class.add_method(Phpmethod('delete', access=Phpmethod.PUBLIC,
			params=['\{} ${}'.format(api_data_class.class_namespace,entity_name_capitalized_after)],
			body="""try {{
						    ${variable}Model = $this->{variable}Factory->create();
						    $this->resource->load(${variable}Model, ${variable}->get{entity_id}());
						    $this->resource->delete(${variable}Model);
					}} catch (\Exception $exception) {{
					    throw new CouldNotDeleteException(__(
					        'Could not delete the {entity_name}: %1',
					        $exception->getMessage()
					    ));
					}}
					return true;
			""".format(variable=entity_name_capitalized_after,entity_name=entity_name,entity_id=entity_id_capitalized),
			docstring=['{@inheritdoc}']
		))
		entity_repository_class.add_method(Phpmethod('deleteById', access=Phpmethod.PUBLIC,
			params=['${}Id'.format(entity_name_capitalized_after)],
			body="""return $this->delete($this->getById(${variable}Id));
			""".format(variable=entity_name_capitalized_after,entity_name=entity_name),
			docstring=['{@inheritdoc}']
		))
		self.add_class(entity_repository_class)

		# Create Data Model Class
		data_entity_class = Phpclass('Model\\Data\\' + entity_name_capitalized.replace('_', '\\'),
			dependencies=[api_data_class.class_namespace],
			extends='\\Magento\\Framework\\Api\\AbstractExtensibleObject',
			implements=[
				api_data_class.class_name
			])

		data_entity_class.add_method(Phpmethod('get' + entity_id_capitalized,
			docstring=['Get {}'.format(entity_id),'@return {}'.format('string|null')],
			body="""return $this->_get({});
			""".format('self::'+entity_id.upper()),
		))

		data_entity_class.add_method(Phpmethod('set' + entity_id_capitalized,
			params=['${}'.format(entity_id_capitalized_after)],
			docstring=['Set {}'.format(entity_id),'@param string ${}'.format(entity_id_capitalized_after),'@return \{}'.format(api_data_class.class_namespace)],
			body="""return $this->setData({}, ${});
			""".format('self::' + entity_id.upper(), entity_id_capitalized_after)
		))

		data_entity_class.add_method(Phpmethod('get' + field_name_capitalized,
			docstring=['Get {}'.format(field_name),'@return {}'.format('string|null')],
			body="""return $this->_get({});
			""".format('self::' + field_name.upper()),
		))

		data_entity_class.add_method(Phpmethod('set' + field_name_capitalized,
			params=['${}'.format(lowerfirst(field_name_capitalized))],
			docstring=['Set {}'.format(field_name),'@param string ${}'.format(lowerfirst(field_name_capitalized)),'@return \{}'.format(api_data_class.class_namespace)],
			body="""return $this->setData({}, ${});
			""".format('self::' + field_name.upper(), lowerfirst(field_name_capitalized))
		))

		data_entity_class.add_method(Phpmethod('getExtensionAttributes',
			docstring=['Retrieve existing extension attributes object or create a new one.','@return '+ extension_interface_class_name +'|null'],
			body="""return $this->_getExtensionAttributes();
			"""
		))

		data_entity_class.add_method(Phpmethod('setExtensionAttributes',
			params=[extension_interface_class_name + ' $extensionAttributes'],
			docstring=['Set an extension attributes object.','@param ' + extension_interface_class_name +' $extensionAttributes','@return $this'],
			body="""return $this->_setExtensionAttributes($extensionAttributes);
			"""
		))
		self.add_class(data_entity_class)

		# Create di.xml preferences
		self.add_xml('etc/di.xml', Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:framework:ObjectManager/etc/config.xsd"}, nodes=[
		    Xmlnode('preference', attributes={
		        'for': "{}\\{}\\Api\\{}RepositoryInterface".format(self._module.package, self._module.name, entity_name_capitalized),
		        'type': entity_repository_class.class_namespace
		    }),
		    Xmlnode('preference', attributes={
		        'for': "{}\\{}\\Api\\Data\\{}Interface".format(self._module.package, self._module.name, entity_name_capitalized),
		        'type': "{}\\{}\\Model\\Data\\{}".format(self._module.package, self._module.name, entity_name_capitalized)
		    }),
		    Xmlnode('preference', attributes={
		        'for': "{}\\{}\\Api\\Data\\{}SearchResultsInterface".format(self._module.package, self._module.name, entity_name_capitalized),
		        'type': 'Magento\Framework\Api\SearchResults'
		    })
		]))

		# add grid
		if adminhtml_grid:
			self.add_adminhtml_grid(entity_name, field_name, entity_table, entity_id, collection_entity_class, field_element_type, top_level_menu, adminhtml_form)

		if adminhtml_form:
			self.add_adminhtml_form(entity_name, field_name, entity_table, entity_id, collection_entity_class, entity_class, required, field_element_type)
			self.add_acl(entity_name)


		if web_api:
			self.add_web_api(entity_name, field_name, entity_table, entity_id, collection_entity_class, entity_class, required, field_element_type, api_repository_class, entity_id_capitalized_after)

		if web_api | adminhtml_form | adminhtml_grid:
			self.add_acl(entity_name)

	def add_adminhtml_grid(self, entity_name, field_name, entity_table, entity_id, collection_entity_class, field_element_type, top_level_menu, adminhtml_form):
		frontname = self.module_name.lower()
		data_source_id = '{}_listing_data_source'.format(entity_table)

		# create controller
		index_controller_class = Phpclass('Controller\\Adminhtml\\' + entity_name.replace('_', '') + '\\Index', extends='\\Magento\\Backend\\App\\Action',
			attributes=[
			'protected $resultPageFactory;'
			])

		index_controller_class.add_method(Phpmethod('__construct',
			params=['\\Magento\\Backend\\App\\Action\\Context $context', '\\Magento\\Framework\\View\\Result\\PageFactory $resultPageFactory'],
			body='$this->resultPageFactory = $resultPageFactory;\nparent::__construct($context);',
			docstring=[
				'Constructor',
				'',
				'@param \\Magento\\Backend\\App\\Action\\Context $context',
				'@param \\Magento\\Framework\\View\\Result\\PageFactory $resultPageFactory',
			]))

		index_controller_class.add_method(Phpmethod('execute',
			body_return="""
			$resultPage = $this->resultPageFactory->create();
			$resultPage->getConfig()->getTitle()->prepend(__("{entity_name}"));
			return $resultPage;
			""".format(entity_name=entity_name),
			docstring=[
				'Index action',
				'',
				'@return \Magento\Framework\Controller\ResultInterface',
			]))

		self.add_class(index_controller_class)

		# create menu.xml
		top_level_menu_node = False
		if top_level_menu:
			top_level_menu_node = Xmlnode('add', attributes={
				'id': "{}::top_level".format(self._module.package),
				'title': self._module.package,
				'module': self.module_name,
				'sortOrder': 9999,
				'resource': 'Magento_Backend::content',
			})

		self.add_xml('etc/adminhtml/menu.xml', Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:module:Magento_Backend:etc/menu.xsd"}, nodes=[
			Xmlnode('menu', nodes=[
				top_level_menu_node,
				Xmlnode('add', attributes={
					'id': "{}::{}".format(self.module_name, entity_table),
					'title': entity_name.replace('_', ' '),
					'module': self.module_name,
					'sortOrder': 9999,
					'resource': 'Magento_Backend::content',
					'parent': '{}::top_level'.format(self._module.package),
					'action': '{}/{}/index'.format(frontname, entity_name.lower().replace('_', ''))
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
				'name': collection_entity_class.class_namespace.replace('Collection', 'Grid\\Collection'),
				'type': 'Magento\\Framework\\View\\Element\\UiComponent\\DataProvider\\SearchResult',
				}, nodes=[
				Xmlnode('arguments', nodes=[
					Xmlnode('argument', attributes={'name': 'mainTable', 'xsi:type': 'string'}, node_text=entity_table),
					Xmlnode('argument', attributes={'name': 'resourceModel', 'xsi:type': 'string'}, node_text= collection_entity_class.class_namespace),
				])
			]),
			Xmlnode('type', attributes={'name': 'Magento\\Framework\\View\\Element\\UiComponent\\DataProvider\\CollectionFactory'}, nodes=[
				Xmlnode('arguments', nodes=[
					Xmlnode('argument', attributes={'name': 'collections', 'xsi:type': 'array'}, nodes=[
						Xmlnode('item', attributes={'name': data_source_id, 'xsi:type': 'string'}, node_text=collection_entity_class.class_namespace.replace('Collection', 'Grid\\Collection'))
					])
				])
			])
		]))

		# create layout.xml
		self.add_xml('view/adminhtml/layout/{}_{}_index.xml'.format(frontname, entity_name.replace('_', '').lower()),
			Xmlnode('page', attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:framework:View/Layout/etc/page_configuration.xsd"}, nodes=[
				Xmlnode('update', attributes={'handle': 'styles'}),
				Xmlnode('body', nodes=[
					Xmlnode('referenceContainer', attributes={'name': 'content'}, nodes=[
						Xmlnode('uiComponent', attributes={'name': '{}_listing'.format(entity_table)})
					])
				])
			]))

		# create components.xml
		data_source_xml = Xmlnode('dataSource', attributes={'name': data_source_id, 'component': 'Magento_Ui/js/grid/provider'}, nodes=[
			Xmlnode('settings', nodes=[
				Xmlnode('updateUrl', attributes={'path': 'mui/index/render'})
			]),
			Xmlnode('aclResource', node_text='{}_{}::{}'.format(self._module.package, self._module.name, entity_name)),
			Xmlnode('dataProvider', attributes={'name': data_source_id,'class': 'Magento\\Framework\\View\\Element\\UiComponent\\DataProvider\\DataProvider'}, nodes=[
				Xmlnode('settings', nodes=[
					Xmlnode('requestFieldName', node_text='id'),
					Xmlnode('primaryFieldName', node_text=entity_id)
				])
			])
		])

		if adminhtml_form:
			columns_settings_xml = Xmlnode('settings', nodes=[
				Xmlnode('editorConfig', nodes=[
					Xmlnode('param', attributes={'name': 'selectProvider', 'xsi:type': 'string'}, node_text='{0}_listing.{0}_listing.{0}_columns.ids'.format(entity_table)),
					Xmlnode('param', attributes={'name': 'enabled', 'xsi:type': 'boolean'}, node_text='true'),
					Xmlnode('param', attributes={'name': 'indexField', 'xsi:type': 'string'}, node_text=entity_id),
					Xmlnode('param', attributes={'name': 'clientConfig', 'xsi:type': 'array'}, nodes=[
						Xmlnode('item', attributes={'name': 'saveUrl', 'xsi:type': 'url', 'path': '{}/{}/inlineEdit'.format(frontname, entity_name.replace('_', ''))}),
						Xmlnode('item', attributes={'name': 'validateBeforeSave', 'xsi:type': 'boolean'}, node_text='false'),
					]),
				]),
				Xmlnode('childDefaults', nodes=[
					Xmlnode('param', attributes={'name': 'fieldAction', 'xsi:type': 'array'}, nodes=[
						Xmlnode('item', attributes={'name': 'provider', 'xsi:type': 'string'}, node_text='{0}_listing.{0}_listing.{0}_columns_editor'.format(entity_table)),
						Xmlnode('item', attributes={'name': 'target', 'xsi:type': 'string'}, node_text='startEdit'),
						Xmlnode('item', attributes={'name': 'params', 'xsi:type': 'array'}, nodes=[
							Xmlnode('item', attributes={'name': '0', 'xsi:type': 'string'}, node_text='${ $.$data.rowIndex }'),
							Xmlnode('item', attributes={'name': '1', 'xsi:type': 'boolean'}, node_text='true'),
						]),
					]),
				]),
			])

		columns_xml = Xmlnode('columns', attributes={'name': '{}_columns'.format(entity_table)}, nodes=[
			Xmlnode('selectionsColumn', attributes={'name': 'ids'}, nodes=[
				Xmlnode('settings', nodes=[
					Xmlnode('indexField', node_text=entity_id)
				]),
			]),
			Xmlnode('column', attributes={'name': entity_id}, nodes=[
				Xmlnode('settings', nodes=[
					Xmlnode('filter', node_text='text'),
					Xmlnode('sorting', node_text='asc'),
					Xmlnode('label', attributes={'translate': 'true'}, node_text='ID')
				])
			]),
			Xmlnode('column', attributes={'name': field_name}, nodes=[
				Xmlnode('settings', nodes=[
					Xmlnode('filter', node_text='text'),
					Xmlnode('label', attributes={'translate': 'true'}, node_text=field_name)
				])
			])
		])

		if adminhtml_form:
			columns_xml = Xmlnode('columns', attributes={'name': '{}_columns'.format(entity_table)}, nodes=[
				columns_settings_xml,
				Xmlnode('selectionsColumn', attributes={'name': 'ids'}, nodes=[
					Xmlnode('settings', nodes=[
						Xmlnode('indexField', node_text=entity_id)
					]),
				]),
				Xmlnode('column', attributes={'name': entity_id}, nodes=[
					Xmlnode('settings', nodes=[
						Xmlnode('filter', node_text='text'),
						Xmlnode('sorting', node_text='asc'),
						Xmlnode('label', attributes={'translate': 'true'}, node_text='ID')
					])
				]),
				Xmlnode('column', attributes={'name': field_name}, nodes=[
					Xmlnode('settings', nodes=[
						Xmlnode('filter', node_text='text'),
						Xmlnode('label', attributes={'translate': 'true'}, node_text=field_name)
					])
				])
			])

		self.add_xml('view/adminhtml/ui_component/{}_listing.xml'.format(entity_table),
			Xmlnode('listing', attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:module:Magento_Ui:etc/ui_configuration.xsd"}, nodes=[
				Xmlnode('argument', attributes={'name': 'data', 'xsi:type': 'array'}, nodes=[
					Xmlnode('item', attributes={'name': 'js_config', 'xsi:type': 'array'}, nodes=[
						Xmlnode('item', attributes={'name': 'provider', 'xsi:type': 'string'}, node_text='{}_listing.{}'.format(entity_table, data_source_id)),
					]),
				]),
				Xmlnode('settings', nodes=[
					Xmlnode('spinner', node_text='{}_columns'.format(entity_table)),
					Xmlnode('deps', nodes=[
						Xmlnode('dep',node_text='{}_listing.{}'.format(entity_table, data_source_id))
					])
				]),
				data_source_xml,
				Xmlnode('listingToolbar', attributes={'name': 'listing_top'}, nodes=[
					Xmlnode('settings', nodes=[
						Xmlnode('sticky', node_text='true'),
					]),
					Xmlnode('bookmark', attributes={'name': 'bookmarks'}),
					Xmlnode('columnsControls', attributes={'name': 'columns_controls'}),
					Xmlnode('filters', attributes={'name': 'listing_filters'}),
					Xmlnode('paging', attributes={'name': 'listing_paging'})
				]),
				columns_xml
			]))

	def add_adminhtml_form(self, entity_name, field_name, entity_table, entity_id, collection_entity_class, entity_class, required, field_element_type):
		frontname = self.module_name.lower()
		# Add block buttons
		# Back button
		back_button = Phpclass('Block\\Adminhtml\\' + entity_name.replace('_', '\\') + '\\Edit\\BackButton', implements=['ButtonProviderInterface'],
			extends='GenericButton',
			dependencies=['Magento\\Framework\\View\\Element\\UiComponent\\Control\\ButtonProviderInterface'])
		back_button.add_method(Phpmethod('getButtonData',
			body="""return [
				    'label' => __('Back'),
				    'on_click' => sprintf("location.href = '%s';", $this->getBackUrl()),
				    'class' => 'back',
				    'sort_order' => 10
				];""",
			docstring=['@return array']))
		back_button.add_method(Phpmethod('getBackUrl',
			body="""return $this->getUrl('*/*/');""",
			docstring=[
				'Get URL for back (reset) button',
				'',
				'@return string'
			]))
		self.add_class(back_button)

		# Delete button
		delete_button = Phpclass('Block\\Adminhtml\\' + entity_name.replace('_', '\\') + '\\Edit\\DeleteButton', implements=['ButtonProviderInterface'],
			extends='GenericButton',
			dependencies=['Magento\\Framework\\View\\Element\\UiComponent\\Control\\ButtonProviderInterface'])
		delete_button.add_method(Phpmethod('getButtonData',
			body="""$data = [];
				if ($this->getModelId()) {{
				    $data = [
				        'label' => __('Delete {}'),
				        'class' => 'delete',
				        'on_click' => 'deleteConfirm(\\'' . __(
				            'Are you sure you want to do this?'
				        ) . '\\', \\'' . $this->getDeleteUrl() . '\\')',
				        'sort_order' => 20,
				    ];
				}}
				return $data;""".format(entity_name.replace('_', ' ').title()),
			docstring=['@return array']))
		delete_button.add_method(Phpmethod('getDeleteUrl',
			body="""return $this->getUrl('*/*/delete', ['{}' => $this->getModelId()]);""".format(entity_id),
			docstring=[
				'Get URL for delete button',
				'',
				'@return string'
			]))
		self.add_class(delete_button)

		# Generic button
		generic_button = Phpclass('Block\\Adminhtml\\' + entity_name.replace('_', '\\') + '\\Edit\\GenericButton',
			dependencies=['Magento\\Backend\\Block\Widget\\Context'],
			attributes=[
				'protected $context;'
			],
			abstract=True)
		generic_button.add_method(Phpmethod('__construct',
			params=['Context $context'],
			body="""$this->context = $context;""",
			docstring=['@param \\Magento\\Backend\\Block\Widget\\Context $context']))

		generic_button.add_method(Phpmethod('getModelId',
			body="""return $this->context->getRequest()->getParam('{}');""".format(entity_id),
			docstring=[
				'Return model ID',
				'',
				'@return int|null'
			]))
		generic_button.add_method(Phpmethod('getUrl', params=["$route = ''","$params = []"],
			body="""return $this->context->getUrlBuilder()->getUrl($route, $params);""",
			docstring=[
				'Generate url by route and parameters',
				'',
				'@param   string $route',
				'@param   array $params',
				'@return  string'
			]
			))
		self.add_class(generic_button)

		# Save and continu button
		save_continue_button = Phpclass('Block\\Adminhtml\\' + entity_name.replace('_', '\\') + '\\Edit\\SaveAndContinueButton', implements=['ButtonProviderInterface'],
			extends='GenericButton',
			dependencies=['Magento\\Framework\\View\\Element\\UiComponent\\Control\\ButtonProviderInterface'])
		save_continue_button.add_method(Phpmethod('getButtonData',
			body="""return [
				    'label' => __('Save and Continue Edit'),
				    'class' => 'save',
				    'data_attribute' => [
				        'mage-init' => [
				            'button' => ['event' => 'saveAndContinueEdit'],
				        ],
				    ],
				    'sort_order' => 80,
				];""",
			docstring=[
				'@return array'
			]))
		self.add_class(save_continue_button)


		# Save  button
		save_button = Phpclass('Block\\Adminhtml\\' + entity_name.replace('_', '\\') + '\\Edit\\SaveButton', implements=['ButtonProviderInterface'],
			extends='GenericButton',
			dependencies=['Magento\\Framework\\View\\Element\\UiComponent\\Control\\ButtonProviderInterface'])
		save_button.add_method(Phpmethod('getButtonData',
			body="""return [
				    'label' => __('Save {}'),
				    'class' => 'save primary',
				    'data_attribute' => [
				        'mage-init' => ['button' => ['event' => 'save']],
				        'form-role' => 'save',
				    ],
				    'sort_order' => 90,
				];""".format(entity_name.replace('_', ' ').title()),
			docstring=[
				'@return array'
			]))
		self.add_class(save_button)

		# Add controllers
		###########################################################################################
		register_model = self.module_name.lower() + '_' + entity_name.lower()

		# link controller
		link_controller = Phpclass('Controller\\Adminhtml\\' + entity_name.replace('_', ''), extends='\\Magento\\Backend\\App\\Action', abstract=True,
			attributes=[
				"const ADMIN_RESOURCE = '{}::top_level';".format(self.module_name),
				'protected $_coreRegistry;'])
		link_controller.add_method(Phpmethod('__construct',
			params=['\\Magento\\Backend\\App\\Action\\Context $context', '\\Magento\\Framework\\Registry $coreRegistry'],
			body="""$this->_coreRegistry = $coreRegistry;\nparent::__construct($context);""",
			docstring=[
				'@param \\Magento\\Backend\\App\\Action\\Context $context',
				'@param \\Magento\\Framework\\Registry $coreRegistry'
			]))
		link_controller.add_method(Phpmethod('initPage', params=['$resultPage'],
			body="""$resultPage->setActiveMenu(self::ADMIN_RESOURCE)
				    ->addBreadcrumb(__('{namespace}'), __('{namespace}'))
				    ->addBreadcrumb(__('{entity_name}'), __('{entity_name}'));
				return $resultPage;""".format(
					namespace = self._module.package,
					entity_name = entity_name.replace('_', ' ').title()
				),
			docstring=[
				'Init page',
				'',
				'@param \Magento\Backend\Model\View\Result\Page $resultPage',
				'@return \Magento\Backend\Model\View\Result\Page'
			]))
		self.add_class(link_controller)

		# Delete controller
		delete_controller = Phpclass('Controller\\Adminhtml\\' + entity_name.replace('_', '') + '\\Delete', extends='\\' + link_controller.class_namespace)
		delete_controller.add_method(Phpmethod('execute',
			body="""/** @var \Magento\Backend\Model\View\Result\Redirect $resultRedirect */
					$resultRedirect = $this->resultRedirectFactory->create();
					// check if we know what should be deleted
					$id = $this->getRequest()->getParam('{entity_id}');
					if ($id) {{
					    try {{
					        // init model and delete
					        $model = $this->_objectManager->create(\{entity_class}::class);
					        $model->load($id);
					        $model->delete();
					        // display success message
					        $this->messageManager->addSuccessMessage(__('You deleted the {entity_name}.'));
					        // go to grid
					        return $resultRedirect->setPath('*/*/');
					    }} catch (\Exception $e) {{
					        // display error message
					        $this->messageManager->addErrorMessage($e->getMessage());
					        // go back to edit form
					        return $resultRedirect->setPath('*/*/edit', ['{entity_id}' => $id]);
					    }}
					}}
					// display error message
					$this->messageManager->addErrorMessage(__('We can\\\'t find a {entity_name} to delete.'));
					// go to grid
					return $resultRedirect->setPath('*/*/');""".format(
						entity_id = entity_id,
						entity_class = entity_class.class_namespace,
						entity_name = entity_name.replace('_', ' ').title()),
			docstring=[
				'Delete action',
				'',
				'@return \Magento\Framework\Controller\ResultInterface',
			]
					))
		self.add_class(delete_controller)

		# Edit controller
		edit_controller = Phpclass('Controller\\Adminhtml\\' + entity_name.replace('_', '') + '\\Edit', extends= '\\' + link_controller.class_namespace,
			attributes=[
				'protected $resultPageFactory;'
			])
		edit_controller.add_method(Phpmethod('__construct',
			params=['\\Magento\\Backend\\App\\Action\\Context $context',
				'\\Magento\\Framework\\Registry $coreRegistry',
				'\\Magento\\Framework\\View\\Result\\PageFactory $resultPageFactory'],
			body="""$this->resultPageFactory = $resultPageFactory;\nparent::__construct($context, $coreRegistry);""",
			docstring=[
				'@param \\Magento\\Backend\\App\\Action\\Context $context',
				'@param \\Magento\\Framework\\Registry $coreRegistry',
				'@param \\Magento\\Framework\\View\\Result\\PageFactory $resultPageFactory',
			]))
		edit_controller.add_method(Phpmethod('execute',
			body="""// 1. Get ID and create model
				$id = $this->getRequest()->getParam('{entity_id}');
				$model = $this->_objectManager->create(\{entity_class}::class);

				// 2. Initial checking
				if ($id) {{
				    $model->load($id);
				    if (!$model->getId()) {{
				        $this->messageManager->addErrorMessage(__('This {entity_name} no longer exists.'));
				        /** @var \Magento\Backend\Model\View\Result\Redirect $resultRedirect */
				        $resultRedirect = $this->resultRedirectFactory->create();
				        return $resultRedirect->setPath('*/*/');
				    }}
				}}
				$this->_coreRegistry->register('{register_model}', $model);

				// 3. Build edit form
				/** @var \Magento\Backend\Model\View\Result\Page $resultPage */
				$resultPage = $this->resultPageFactory->create();
				$this->initPage($resultPage)->addBreadcrumb(
				    $id ? __('Edit {entity_name}') : __('New {entity_name}'),
				    $id ? __('Edit {entity_name}') : __('New {entity_name}')
				);
				$resultPage->getConfig()->getTitle()->prepend(__('{entity_name}s'));
				$resultPage->getConfig()->getTitle()->prepend($model->getId() ? __('Edit {entity_name} %1', $model->getId()) : __('New {entity_name}'));
				return $resultPage;""".format(
						entity_id = entity_id,
						entity_class = entity_class.class_namespace,
						entity_name = entity_name.replace('_', ' ').title(),
						register_model = register_model
					),
			docstring=[
				'Edit action',
				'',
				'@return \Magento\Framework\Controller\ResultInterface',
			]))
		self.add_class(edit_controller)

		# Inline Controller
		inline_edit_controller = Phpclass('Controller\\Adminhtml\\' + entity_name.replace('_', '') + '\\InlineEdit', extends='\\Magento\\Backend\\App\\Action',
			attributes=[
				'protected $jsonFactory;'
			])
		inline_edit_controller.add_method(Phpmethod('__construct',
			params=['\\Magento\\Backend\\App\\Action\\Context $context',
				'\\Magento\\Framework\\Controller\\Result\\JsonFactory $jsonFactory'],
			body="""parent::__construct($context);\n$this->jsonFactory = $jsonFactory;""",
			docstring=[
				'@param \\Magento\\Backend\\App\\Action\\Context $context',
				'@param \\Magento\\Framework\\Controller\\Result\\JsonFactory $jsonFactory',
			]))
		inline_edit_controller.add_method(Phpmethod('execute',
			body="""/** @var \Magento\Framework\Controller\Result\Json $resultJson */
					$resultJson = $this->jsonFactory->create();
					$error = false;
					$messages = [];

					if ($this->getRequest()->getParam('isAjax')) {{
					    $postItems = $this->getRequest()->getParam('items', []);
					    if (!count($postItems)) {{
					        $messages[] = __('Please correct the data sent.');
					        $error = true;
					    }} else {{
					        foreach (array_keys($postItems) as $modelid) {{
					            /** @var \{entity_class} $model */
					            $model = $this->_objectManager->create(\{entity_class}::class)->load($modelid);
					            try {{
					                $model->setData(array_merge($model->getData(), $postItems[$modelid]));
					                $model->save();
					            }} catch (\Exception $e) {{
					                $messages[] = "[{entity_name} ID: {{$modelid}}]  {{$e->getMessage()}}";
					                $error = true;
					            }}
					        }}
					    }}
					}}

					return $resultJson->setData([
					    'messages' => $messages,
					    'error' => $error
					]);""".format(
						entity_class = entity_class.class_namespace,
						entity_name = entity_name.replace('_', ' ').title(),
					),
			docstring=[
				'Inline edit action',
				'',
				'@return \Magento\Framework\Controller\ResultInterface',
			]))
		self.add_class(inline_edit_controller)

		# new Controller
		new_controller = Phpclass('Controller\\Adminhtml\\' + entity_name.replace('_', '') + '\\NewAction', extends='\\' + link_controller.class_namespace,
			attributes=[
				'protected $resultForwardFactory;'
			])
		new_controller.add_method(Phpmethod('__construct',
			params=['\\Magento\\Backend\\App\\Action\\Context $context',
				'\\Magento\\Framework\\Registry $coreRegistry',
				'\\Magento\\Backend\\Model\\View\\Result\\ForwardFactory $resultForwardFactory'],
			body="""$this->resultForwardFactory = $resultForwardFactory;\nparent::__construct($context, $coreRegistry);""",
			docstring=[
				'@param \\Magento\\Backend\\App\\Action\\Context $context',
				'@param \\Magento\\Framework\\Registry $coreRegistry',
				'@param \\Magento\\Backend\\Model\\View\\Result\\ForwardFactory $resultForwardFactory',
			]))
		new_controller.add_method(Phpmethod('execute',
			body="""/** @var \Magento\Framework\Controller\Result\Forward $resultForward */
					$resultForward = $this->resultForwardFactory->create();
					return $resultForward->forward('edit');""",
			docstring=[
				'New action',
				'',
				'@return \Magento\Framework\Controller\ResultInterface',
			]))
		self.add_class(new_controller)

		# Save Controller
		new_controller = Phpclass('Controller\\Adminhtml\\' + entity_name.replace('_', '') + '\\Save', dependencies=['Magento\Framework\Exception\LocalizedException'], extends='\\Magento\\Backend\\App\\Action',
			attributes=[
				'protected $dataPersistor;'])
		new_controller.add_method(Phpmethod('__construct',
			params=['\\Magento\\Backend\\App\\Action\\Context $context',
				'\\Magento\\Framework\\App\\Request\\DataPersistorInterface $dataPersistor'],
			body="""$this->dataPersistor = $dataPersistor;\nparent::__construct($context);""",
			docstring=[
				'@param \\Magento\\Backend\\App\\Action\\Context $context',
				'@param \\Magento\\Framework\\App\\Request\\DataPersistorInterface $dataPersistor',
			]))
		new_controller.add_method(Phpmethod('execute',
			body="""/** @var \Magento\Backend\Model\View\Result\Redirect $resultRedirect */
					$resultRedirect = $this->resultRedirectFactory->create();
					$data = $this->getRequest()->getPostValue();
					if ($data) {{
					    $id = $this->getRequest()->getParam('{entity_id}');

					    $model = $this->_objectManager->create(\{entity_class}::class)->load($id);
					    if (!$model->getId() && $id) {{
					        $this->messageManager->addErrorMessage(__('This {entity_name} no longer exists.'));
					        return $resultRedirect->setPath('*/*/');
					    }}
									
					    $model->setData($data);

					    try {{
					        $model->save();
					        $this->messageManager->addSuccessMessage(__('You saved the {entity_name}.'));
					        $this->dataPersistor->clear('{register_model}');

					        if ($this->getRequest()->getParam('back')) {{
					            return $resultRedirect->setPath('*/*/edit', ['{entity_id}' => $model->getId()]);
					        }}
					        return $resultRedirect->setPath('*/*/');
					    }} catch (LocalizedException $e) {{
					        $this->messageManager->addErrorMessage($e->getMessage());
					    }} catch (\Exception $e) {{
					        $this->messageManager->addExceptionMessage($e, __('Something went wrong while saving the {entity_name}.'));
					    }}

					    $this->dataPersistor->set('{register_model}', $data);
					    return $resultRedirect->setPath('*/*/edit', ['{entity_id}' => $this->getRequest()->getParam('{entity_id}')]);
					}}
					return $resultRedirect->setPath('*/*/');""".format(
						entity_id = entity_id,
						entity_class = entity_class.class_namespace,
						entity_name = entity_name.replace('_', ' ').title(),
						register_model = register_model
					),
			docstring=[
				'Save action',
				'',
				'@return \Magento\Framework\Controller\ResultInterface',
			]))
		self.add_class(new_controller)

		# Add model provider
		data_provider = Phpclass('Model\\' + entity_name.replace('_', '') + '\\DataProvider', extends='\\Magento\\Ui\\DataProvider\\AbstractDataProvider',
			attributes=[
				'protected $collection;\n',
				'protected $dataPersistor;\n',
				'protected $loadedData;'
			],
			dependencies=[collection_entity_class.class_namespace + 'Factory', 'Magento\\Framework\\App\\Request\\DataPersistorInterface'])
		data_provider.add_method(Phpmethod('__construct',
			params=['$name',
				'$primaryFieldName',
				'$requestFieldName',
				'CollectionFactory $collectionFactory',
				'DataPersistorInterface $dataPersistor',
				'array $meta = []',
				'array $data = []'],
			body="""$this->collection = $collectionFactory->create();
					$this->collection->addAttributeToSelect('*');
					$this->dataPersistor = $dataPersistor;
					parent::__construct($name, $primaryFieldName, $requestFieldName, $meta, $data);""",
			docstring=[
				'Constructor',
				'',
				'@param string $name',
				'@param string $primaryFieldName',
				'@param string $requestFieldName',
				'@param CollectionFactory $collectionFactory',
				'@param DataPersistorInterface $dataPersistor',
				'@param array $meta',
				'@param array $data'
			]))
		data_provider.add_method(Phpmethod('getData',
			body="""if (isset($this->loadedData)) {{
					    return $this->loadedData;
					}}
					$items = $this->collection->getItems();
					foreach ($items as $model) {{
					    $this->loadedData[$model->getId()] = $model->getData();
					}}
					$data = $this->dataPersistor->get('{register_model}');

					if (!empty($data)) {{
					    $model = $this->collection->getNewEmptyItem();
					    $model->setData($data);
					    $this->loadedData[$model->getId()] = $model->getData();
					    $this->dataPersistor->clear('{register_model}');
					}}

					return $this->loadedData;""".format(
						register_model = register_model
					),
			docstring=[
				'Get data',
				'',
				'@return array',
			]))

		self.add_class(data_provider)

		# Add model actions
		actions = Phpclass('Ui\Component\Listing\Column\\' + entity_name.replace('_', '') + 'Actions', extends='\\Magento\\Ui\\Component\\Listing\\Columns\Column',
			attributes=[
				"const URL_PATH_EDIT = '{}/{}/edit';".format(frontname, entity_name.replace('_', '').lower()),
				"const URL_PATH_DELETE = '{}/{}/delete';".format(frontname, entity_name.replace('_', '').lower()),
				"const URL_PATH_DETAILS = '{}/{}/details';".format(frontname, entity_name.replace('_', '').lower()),
				'protected $urlBuilder;',
			])
		actions.add_method(Phpmethod('__construct',
			params=['\\Magento\\Framework\\View\\Element\\UiComponent\\ContextInterface $context',
				'\\Magento\\Framework\\View\\Element\\UiComponentFactory $uiComponentFactory',
				'\\Magento\\Framework\\UrlInterface $urlBuilder',
				'array $components = []',
				'array $data = []'],
			body="""$this->urlBuilder = $urlBuilder;\nparent::__construct($context, $uiComponentFactory, $components, $data);""",
			docstring=[
				'@param \\Magento\\Framework\\View\\Element\\UiComponent\\ContextInterface $context',
				'@param \\Magento\\Framework\\View\\Element\\UiComponentFactory $uiComponentFactory',
				'@param \\Magento\\Framework\\UrlInterface $urlBuilder',
				'@param array $components',
				'@param array $data'
			]))
		actions.add_method(Phpmethod('prepareDataSource', params=['array $dataSource'],
			body="""if (isset($dataSource['data']['items'])) {{
					    foreach ($dataSource['data']['items'] as & $item) {{
					        if (isset($item['{entity_id}'])) {{
					            $item[$this->getData('name')] = [
					                'edit' => [
					                    'href' => $this->urlBuilder->getUrl(
					                        static::URL_PATH_EDIT,
					                        [
					                            '{entity_id}' => $item['{entity_id}']
					                        ]
					                    ),
					                    'label' => __('Edit')
					                ],
					                'delete' => [
					                    'href' => $this->urlBuilder->getUrl(
					                        static::URL_PATH_DELETE,
					                        [
					                            '{entity_id}' => $item['{entity_id}']
					                        ]
					                    ),
					                    'label' => __('Delete'),
					                    'confirm' => [
					                        'title' => __('Delete "${{ $.$data.title }}"'),
					                        'message' => __('Are you sure you wan\\\'t to delete a "${{ $.$data.title }}" record?')
					                    ]
					                ]
					            ];
					        }}
					    }}
					}}

					return $dataSource;""".format(
						entity_id = entity_id
					),
			docstring=[
				'Prepare Data Source',
				'',
				'@param array $dataSource',
				'@return array'
			]))
		self.add_class(actions)

		# Edit layout
		self.add_xml('view/adminhtml/layout/{}_{}_edit.xml'.format(frontname, entity_name.replace('_', '').lower()),
			Xmlnode('page', attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:framework:View/Layout/etc/page_configuration.xsd"}, nodes=[
				Xmlnode('update', attributes={'handle': 'styles'}),
				Xmlnode('body', nodes=[
					Xmlnode('referenceContainer', attributes={'name': 'content'}, nodes=[
						Xmlnode('uiComponent', attributes={'name': '{}_form'.format(entity_table)})
					])
				])
			]))

		# New layout
		self.add_xml('view/adminhtml/layout/{}_{}_new.xml'.format(frontname, entity_name.replace('_', '').lower()),
			Xmlnode('page', attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:framework:View/Layout/etc/page_configuration.xsd"}, nodes=[
				Xmlnode('update', attributes={'handle': '{}_{}_edit'.format(frontname, entity_name.lower())})
			]))

		# UI Component Form
		data_source = '{}_form_data_source'.format(entity_name.lower())
		ui_form = Xmlnode('form', attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:module:Magento_Ui:etc/ui_configuration.xsd"}, nodes=[
			Xmlnode('argument', attributes={'name': 'data', 'xsi:type': 'array'}, nodes=[
				Xmlnode('item', attributes={'name': 'js_config', 'xsi:type': 'array'}, nodes=[
					Xmlnode('item', attributes={'name': 'provider', 'xsi:type': 'string'}, node_text='{}_form.{}'.format(entity_table, data_source)),
				]),
				Xmlnode('item', attributes={'name': 'label', 'xsi:type': 'string', 'translate': 'true'}, node_text='General Information'),
				Xmlnode('item', attributes={'name': 'template', 'xsi:type': 'string'}, node_text='templates/form/collapsible'),
			]),
			Xmlnode('settings', nodes=[
				Xmlnode('buttons', nodes=[
					Xmlnode('button', attributes={'name': 'back', 'class': back_button.class_namespace}),
					Xmlnode('button', attributes={'name': 'delete', 'class': delete_button.class_namespace}),
					Xmlnode('button', attributes={'name': 'save', 'class': save_button.class_namespace}),
					Xmlnode('button', attributes={'name': 'save_and_continue', 'class': save_continue_button.class_namespace}),
				]),
				Xmlnode('namespace', node_text='{}_form'.format(entity_table)),
				Xmlnode('dataScope', node_text='data'),
				Xmlnode('deps', nodes=[
					Xmlnode('dep', node_text='{}_form.{}'.format(entity_table, data_source)),
				]),
			]),
			Xmlnode('dataSource', attributes={'name': data_source}, nodes=[
				Xmlnode('argument', attributes={'name': 'data', 'xsi:type': 'array'}, nodes=[
					Xmlnode('item', attributes={'name': 'js_config', 'xsi:type': 'array'}, nodes=[
						Xmlnode('item', attributes={'name': 'component', 'xsi:type': 'string'}, node_text='Magento_Ui/js/form/provider'),
					]),
				]),
				Xmlnode('settings', nodes=[
					Xmlnode('submitUrl', attributes={'path': '*/*/save'}),
				]),
				Xmlnode('dataProvider', attributes={'name': data_source, 'class': data_provider.class_namespace}, nodes=[
					Xmlnode('settings', nodes=[
						Xmlnode('requestFieldName', node_text=entity_id),
						Xmlnode('primaryFieldName', node_text=entity_id),
					]),
				]),
			]),
			Xmlnode('fieldset', attributes={'name': 'general'}, nodes=[
				Xmlnode('settings', nodes=[
					Xmlnode('label', node_text='General'),
				]),
				Xmlnode('field', attributes={'name': field_name, 'formElement': field_element_type, 'sortOrder': str(10 * self.count)}, nodes=[
					Xmlnode('argument', attributes={'name': 'data', 'xsi:type': 'array'}, nodes=[
						Xmlnode('item', attributes={'name': 'config', 'xsi:type': 'array'}, nodes=[
							Xmlnode('item', attributes={'name': 'source', 'xsi:type': 'string'}, node_text=entity_name),
						]),
					]),
					Xmlnode('settings', nodes=[
						Xmlnode('dataType', node_text='text'),
						Xmlnode('label', attributes={'translate': 'true'}, node_text=field_name),
						Xmlnode('dataScope', node_text=field_name),
						Xmlnode('validation', nodes=[
							Xmlnode('rule', attributes={'name': 'required-entry', 'xsi:type': 'boolean'}, node_text= 'true' if required else 'false'),
						]),
					]),
				]),
			]),
		])
		self.add_xml('view/adminhtml/ui_component/{}_form.xml'.format(entity_table), ui_form)

		# Set UI Component Listing
		ui_listing = Xmlnode('listing', attributes={
			'xsi:noNamespaceSchemaLocation': "urn:magento:module:Magento_Ui:etc/ui_configuration.xsd"}, nodes=[
			Xmlnode('settings', nodes=[
				Xmlnode('buttons', nodes=[
					Xmlnode('button', attributes={'name': 'add'}, nodes=[
						Xmlnode('url', attributes={'path': '*/*/new'}),
						Xmlnode('class', node_text='primary'),
						Xmlnode('label', attributes={'translate': 'true'}, node_text='Add new {}'.format(entity_name)),
					]),
				]),
			]),
			Xmlnode('columns', attributes={'name': '{}_columns'.format(entity_table)}, nodes=[
				Xmlnode('column', attributes={'name': field_name}, nodes=[
					Xmlnode('settings', nodes=[
						Xmlnode('editor', nodes=[
							Xmlnode('editorType',
									node_text=field_element_type if field_element_type == 'date' else 'text'),
							Xmlnode('validation', nodes=[
								Xmlnode('rule', attributes={'name': 'required-entry', 'xsi:type': 'boolean'},
										node_text='true' if required else 'false'),
							]),
						]),
					]),
				]),
				Xmlnode('actionsColumn', attributes={'name': 'actions', 'class': actions.class_namespace}, nodes=[
					Xmlnode('settings', nodes=[
						Xmlnode('indexField', node_text=entity_id),
						Xmlnode('resizeEnabled', node_text='false'),
						Xmlnode('resizeDefaultWidth', node_text='107'),
					]),
				]),
			]),
		])

		self.add_xml('view/adminhtml/ui_component/{}_listing.xml'.format(entity_table), ui_listing)

		# Update UI Component Listing
		ui_listing = Xmlnode('listing', attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:module:Magento_Ui:etc/ui_configuration.xsd"}, nodes=[
			Xmlnode('settings', nodes=[
				Xmlnode('buttons', nodes=[
					Xmlnode('button', attributes={'name': 'add'}, nodes=[
						Xmlnode('url', attributes={'path':'*/*/new'}),
						Xmlnode('class', node_text='primary'),
						Xmlnode('label', attributes={'translate': 'true'}, node_text='Add new {}'.format(entity_name)),
					]),
				]),
			]),
			Xmlnode('columns', attributes={'name': '{}_columns'.format(entity_table)}, nodes=[
				Xmlnode('column', attributes={'name': field_name}, nodes=[
					Xmlnode('settings', nodes=[
						Xmlnode('editor',  nodes=[
							Xmlnode('editorType', node_text=field_element_type if field_element_type == 'date' else 'text'),
							Xmlnode('validation', nodes=[
								Xmlnode('rule', attributes={'name': 'required-entry', 'xsi:type': 'boolean'}, node_text='true' if required else 'false'),
							]),
						]),
					]),
				]),
				Xmlnode('actionsColumn', attributes={'name': 'actions', 'class': actions.class_namespace}, nodes=[
					Xmlnode('settings', nodes=[
						Xmlnode('indexField', node_text=entity_id),
						Xmlnode('resizeEnabled', node_text='false'),
						Xmlnode('resizeDefaultWidth', node_text='107'),
					]),
				]),
			]),
		])

		self.add_xml('view/adminhtml/ui_component/{}_listing.xml'.format(entity_table), ui_listing)

	def add_web_api(self, entity_name, field_name, entity_table, entity_id, collection_entity_class, entity_class, required, field_element_type, api_repository_class, entity_id_capitalized_after):

		resource = '{}_{}::{}_'.format(self._module.package,self._module.name,entity_name);
		api_url = '/V1/{}-{}/'.format(self._module.package.lower(),self._module.name.lower())

		webapi_xml = Xmlnode('routes', attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Webapi:etc/webapi.xsd"}, nodes=[
			Xmlnode('route', attributes={'url': api_url + entity_name.lower(), 'method': 'POST'},match_attributes={'url','method'},nodes=[
				Xmlnode('service',attributes={'class':api_repository_class.class_namespace,'method':'save'}),
		 		Xmlnode('resources',nodes=[
		 			Xmlnode('resource', attributes={'ref':resource + 'save'})
				])
			]),
			Xmlnode('route', attributes={'url': api_url + entity_name.lower() + '/search', 'method': 'GET'},match_attributes={'url','method'},nodes=[
				Xmlnode('service',attributes={'class':api_repository_class.class_namespace,'method':'getList'}),
		 		Xmlnode('resources',nodes=[
		 			Xmlnode('resource', attributes={'ref':resource + 'view'})
				])
			]),
			Xmlnode('route', attributes={'url': api_url + entity_name.lower() + '/:' + entity_id_capitalized_after, 'method': 'GET'},match_attributes={'url','method'},nodes=[
				Xmlnode('service',attributes={'class':api_repository_class.class_namespace,'method':'getById'}),
		 		Xmlnode('resources',nodes=[
		 			Xmlnode('resource', attributes={'ref':resource + 'view'})
				])
			]),
			Xmlnode('route', attributes={'url': api_url + entity_name.lower() + '/:' + entity_id_capitalized_after, 'method': 'PUT'},match_attributes={'url','method'},nodes=[
				Xmlnode('service',attributes={'class':api_repository_class.class_namespace,'method':'save'}),
		 		Xmlnode('resources',nodes=[
		 			Xmlnode('resource', attributes={'ref':resource + 'update'})
				])
			]),
			Xmlnode('route', attributes={'url': api_url + entity_name.lower() + '/:' + entity_id_capitalized_after, 'method': 'DELETE'},match_attributes={'url','method'},nodes=[
				Xmlnode('service',attributes={'class':api_repository_class.class_namespace,'method':'deleteById'}),
		 		Xmlnode('resources',nodes=[
		 			Xmlnode('resource', attributes={'ref':resource + 'delete'})
				])
			])
		])

		self.add_xml('etc/webapi.xml', webapi_xml)


	def add_acl(self,entity_name):

		namespace = '{}_{}'.format(self._module.package,self._module.name)

		acl_xml = Xmlnode('config', attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:framework:Acl/etc/acl.xsd"}, nodes=[
			Xmlnode('acl',nodes=[
				Xmlnode('resources',nodes=[
					Xmlnode('resource',attributes={'id':'Magento_Backend::admin'},nodes=[
						Xmlnode('resource',attributes={'id':'{}::{}'.format(namespace,entity_name),'title':'{}'.format(entity_name),'sortOrder':"10"}, nodes=[
							Xmlnode('resource',attributes={'id':'{}::{}_{}'.format(namespace,entity_name,'save'),'title':'Save {}'.format(entity_name),'sortOrder':"10"}),
							Xmlnode('resource',attributes={'id':'{}::{}_{}'.format(namespace,entity_name,'delete'),'title':'Delete {}'.format(entity_name),'sortOrder':"20"}),
							Xmlnode('resource',attributes={'id':'{}::{}_{}'.format(namespace,entity_name,'update'),'title':'Update {}'.format(entity_name),'sortOrder':"30"}),
							Xmlnode('resource',attributes={'id':'{}::{}_{}'.format(namespace,entity_name,'view'),'title':'View {}'.format(entity_name),'sortOrder':"40"})
						])
					])
				])
			])
		])

		self.add_xml('etc/acl.xml', acl_xml)


	@classmethod
	def params(cls):
		return [
			SnippetParam(
				name='entity_name',
				description='Example: Blog',
				required=True,
				regex_validator= r'^[a-zA-Z]{1}\w+$',
				error_message='Only alphanumeric and underscore characters are allowed, and need to start with a alphabetic character.',
				repeat=True
			),
			SnippetParam(name='adminhtml_grid', yes_no=True),
			SnippetParam(name='adminhtml_form', yes_no=True),
			SnippetParam(name='web_api', yes_no=True),
		]

	@classmethod
	def extra_params(cls):
		return [
			SnippetParam(
				name='top_level_menu',
				yes_no=True,
				default=True,
				repeat=True
			),
		]

