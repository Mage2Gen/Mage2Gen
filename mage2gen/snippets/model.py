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


# Long boring code to add a lot of PHP classes and xml, only go here if you feel like too bring you happiness down. 
# Or make your day happy that you don't maintain this code :)


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

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.count = 0

	def add(self, model_name, field_name, field_type='text', adminhtml_grid=False, adminhtml_form=False, extra_params=False):
		self.count += 1
		extra_params = extra_params if extra_params else {}
		
		model_table = '{}_{}'.format(self._module.package.lower(), model_name.lower())
		model_id = '{}_id'.format(model_name.lower())

		field_element_type = 'input'

		if field_type == 'boolean':
			field_element_type = 'checkbox'
		elif field_type == 'date' or field_type == 'timestamp':
			field_element_type = 'date'
		
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
		required = False
		if extra_params.get('default'):
			options['default'] = "'{}'".format(extra_params.get('default'))
		if not extra_params.get('nullable'):
			options['nullable'] = extra_params.get('nullable')
			required = not options['nullable']
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
			self.add_adminhtml_grid(model_name, field_name, model_table, model_id, collection_model_class, field_element_type)

		if adminhtml_form:
			self.add_adminhtml_form(model_name, field_name, model_table, model_id, collection_model_class, model_class, required, field_element_type)

	def add_adminhtml_grid(self, model_name, field_name, model_table, model_id, collection_model_class, field_element_type):
		frontname = self.module_name.lower()
		data_source_id = '{}_grid_data_source'.format(model_table) 
		
		# create controller
		index_controller_class = Phpclass('Controller\\Adminhtml\\' + model_name.replace('_', '') + '\\Index', extends='\\Magento\\Backend\\App\\Action',
				attributes=['protected $resultPageFactory;'])
		
		index_controller_class.add_method(Phpmethod('__construct', 
			params=['\\Magento\\Backend\\App\\Action\\Context $context', '\\Magento\\Framework\\View\\Result\\PageFactory $resultPageFactory'],
			body='$this->resultPageFactory = $resultPageFactory;\nparent::__construct($context);'))
		
		index_controller_class.add_method(Phpmethod('execute', body_return='return $this->resultPageFactory->create();'))
		
		self.add_class(index_controller_class)

		# create menu.xml
		self.add_xml('etc/adminhtml/menu.xml', Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:module:Magento_Backend:etc/menu.xsd"}, nodes=[
			Xmlnode('menu', nodes=[
				Xmlnode('add', attributes={
					'id': "{}::top_level".format(self._module.package),
					'title': self._module.package,
					'module': self.module_name,
					'sortOrder': 9999,
					'resource': 'Magento_Backend::content',
				}),
				Xmlnode('add', attributes={
					'id': "{}::{}".format(self._module.package, model_table),
					'title': model_name.replace('_', ' '),
					'module': self.module_name,
					'sortOrder': 9999,
					'resource': 'Magento_Backend::content',
					'parent': '{}::top_level'.format(self._module.package),
					'action': '{}/{}/index'.format(frontname, model_name.lower().replace('_', ''))
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
		self.add_xml('view/adminhtml/layout/{}_{}_index.xml'.format(frontname, model_name.replace('_', '').lower()), 
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
			Xmlnode('argument', attributes={'name': 'data', 'xsi:type': 'array'}),
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
				Xmlnode('listingToolbar', attributes={'name': 'listing_top'}, nodes=[
					Xmlnode('argument', attributes={'name': 'data', 'xsi:type': 'array'}, nodes=[
						Xmlnode('item', attributes={'name': 'config', 'xsi:type': 'array'}, nodes=[
							Xmlnode('item', attributes={'name': 'sticky', 'xsi:type': 'boolean'}, node_text='true'),
						])
					]),
					Xmlnode('bookmark', attributes={'name': 'bookmark'}),
					Xmlnode('columnsControls', attributes={'name': 'columns_controls'}),
					Xmlnode('filters', attributes={'name': 'listing_filters'}),
					Xmlnode('paging', attributes={'name': 'listing_paging'}),
				]),
				columns_xml,
			]))

	def add_adminhtml_form(self, model_name, field_name, model_table, model_id, collection_model_class, model_class, required, field_element_type):
		frontname = self.module_name.lower()
		# Add block buttons
		# Back button
		back_button = Phpclass('Block\\Adminhtml\\' + model_name.replace('_', '\\') + '\\Edit\\BackButton', implements=['ButtonProviderInterface'],
			extends='GenericButton',
			dependencies=['Magento\\Framework\\View\\Element\\UiComponent\\Control\\ButtonProviderInterface'])
		back_button.add_method(Phpmethod('getButtonData',
			body="""return [
				    'label' => __('Back'),
				    'on_click' => sprintf("location.href = '%s';", $this->getBackUrl()),
				    'class' => 'back',
				    'sort_order' => 10
				];"""))
		back_button.add_method(Phpmethod('getBackUrl',
			body="""return $this->getUrl('*/*/');"""))
		self.add_class(back_button)

		# Delete button
		delete_button = Phpclass('Block\\Adminhtml\\' + model_name.replace('_', '\\') + '\\Edit\\DeleteButton', implements=['ButtonProviderInterface'],
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
				return $data;""".format(model_name.replace('_', ' ').title())))
		delete_button.add_method(Phpmethod('getDeleteUrl',
			body="""return $this->getUrl('*/*/delete', ['{}' => $this->getModelId()]);""".format(model_id)))
		self.add_class(delete_button)

		# Generic button
		generic_button = Phpclass('Block\\Adminhtml\\' + model_name.replace('_', '\\') + '\\Edit\\GenericButton',
			dependencies=['Magento\\Backend\\Block\Widget\\Context'], attributes=['protected $context;'],
			abstract=True)
		generic_button.add_method(Phpmethod('__construct',
			params=['Context $context'],
			body="""$this->context = $context;"""))
		
		generic_button.add_method(Phpmethod('getModelId',
			body="""return $this->context->getRequest()->getParam('{}');""".format(model_id)))
		generic_button.add_method(Phpmethod('getUrl', params=["$route = ''","$params = []"],
			body="""return $this->context->getUrlBuilder()->getUrl($route, $params);"""))
		self.add_class(generic_button)

		# Save and continu button
		save_continue_button = Phpclass('Block\\Adminhtml\\' + model_name.replace('_', '\\') + '\\Edit\\SaveAndContinueButton', implements=['ButtonProviderInterface'],
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
				];"""))
		self.add_class(save_continue_button)


		# Save  button
		save_button = Phpclass('Block\\Adminhtml\\' + model_name.replace('_', '\\') + '\\Edit\\SaveButton', implements=['ButtonProviderInterface'],
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
				];""".format(model_name.replace('_', ' ').title())))
		self.add_class(save_button)

		# Add controllers
		###########################################################################################
		register_model = self.module_name.lower() + '_' + model_name.lower()

		# link controller
		link_controller = Phpclass('Controller\\Adminhtml\\' + model_name.replace('_', ''), extends='\\Magento\\Backend\\App\\Action', abstract=True,
			attributes=["const ADMIN_RESOURCE = '{}::top_level';".format(self.module_name),
				'protected $_coreRegistry;'])
		link_controller.add_method(Phpmethod('__construct',
			params=['\\Magento\\Backend\\App\\Action\\Context $context', '\\Magento\\Framework\\Registry $coreRegistry'],
			body="""$this->_coreRegistry = $coreRegistry;\nparent::__construct($context);"""))
		link_controller.add_method(Phpmethod('initPage', params=['$resultPage'],
			body="""$resultPage->setActiveMenu('Experius_Test::top_level')
				    ->addBreadcrumb(__('{namespace}'), __('{namespace}'))
				    ->addBreadcrumb(__('{model_name}'), __('{model_name}'));
				return $resultPage;""".format(
					namespace = self._module.package,
					model_name = model_name.replace('_', ' ').title()
				)))
		self.add_class(link_controller)

		# Delete controller
		delete_controller = Phpclass('Controller\\Adminhtml\\' + model_name.replace('_', '') + '\\Delete', extends='\\' + link_controller.class_namespace)
		delete_controller.add_method(Phpmethod('execute',
			body="""/** @var \Magento\Backend\Model\View\Result\Redirect $resultRedirect */
					$resultRedirect = $this->resultRedirectFactory->create();
					// check if we know what should be deleted
					$id = $this->getRequest()->getParam('{model_id}');
					if ($id) {{
					    try {{
					        // init model and delete
					        $model = $this->_objectManager->create('{model_class}');
					        $model->load($id);
					        $model->delete();
					        // display success message
					        $this->messageManager->addSuccess(__('You deleted the {model_name}.'));
					        // go to grid
					        return $resultRedirect->setPath('*/*/');
					    }} catch (\Exception $e) {{
					        // display error message
					        $this->messageManager->addError($e->getMessage());
					        // go back to edit form
					        return $resultRedirect->setPath('*/*/edit', ['{model_id}' => $id]);
					    }}
					}}
					// display error message
					$this->messageManager->addError(__('We can\\\'t find a {model_name} to delete.'));
					// go to grid
					return $resultRedirect->setPath('*/*/');""".format(
						model_id = model_id,
						model_class = model_class.class_namespace,
						model_name = model_name.replace('_', ' ').title())
					))
		self.add_class(delete_controller)

		# Edit controller
		edit_controller = Phpclass('Controller\\Adminhtml\\' + model_name.replace('_', '') + '\\Edit', extends= '\\' + link_controller.class_namespace, 
			attributes=['protected $resultPageFactory;'])
		edit_controller.add_method(Phpmethod('__construct',
			params=['\\Magento\\Backend\\App\\Action\\Context $context',
				'\\Magento\\Framework\\Registry $coreRegistry',
				'\\Magento\\Framework\\View\\Result\\PageFactory $resultPageFactory'],
			body="""$this->resultPageFactory = $resultPageFactory;\nparent::__construct($context, $coreRegistry);"""))
		edit_controller.add_method(Phpmethod('execute',
			body="""// 1. Get ID and create model
				$id = $this->getRequest()->getParam('{model_id}');
				$model = $this->_objectManager->create('{model_class}');

				// 2. Initial checking
				if ($id) {{
				    $model->load($id);
				    if (!$model->getId()) {{
				        $this->messageManager->addError(__('This {model_name} no longer exists.'));
				        /** @var \Magento\Backend\Model\View\Result\Redirect $resultRedirect */
				        $resultRedirect = $this->resultRedirectFactory->create();
				        return $resultRedirect->setPath('*/*/');
				    }}
				}}
				$this->_coreRegistry->register('{register_model}', $model);

				// 5. Build edit form
				/** @var \Magento\Backend\Model\View\Result\Page $resultPage */
				$resultPage = $this->resultPageFactory->create();
				$this->initPage($resultPage)->addBreadcrumb(
				    $id ? __('Edit {model_name}') : __('New {model_name}'),
				    $id ? __('Edit {model_name}') : __('New {model_name}')
				);
				$resultPage->getConfig()->getTitle()->prepend(__('{model_name}s'));
				$resultPage->getConfig()->getTitle()->prepend($model->getId() ? $model->getTitle() : __('New {model_name}'));
				return $resultPage;""".format(
						model_id = model_id,
						model_class = model_class.class_namespace,
						model_name = model_name.replace('_', ' ').title(),
						register_model = register_model
					)))
		self.add_class(edit_controller)

		# Inline Controller
		inline_edit_controller = Phpclass('Controller\\Adminhtml\\' + model_name.replace('_', '') + '\\InlineEdit', extends='\\Magento\\Backend\\App\\Action', 
			attributes=['protected $jsonFactory;'])
		inline_edit_controller.add_method(Phpmethod('__construct',
			params=['\\Magento\\Backend\\App\\Action\\Context $context',
				'\\Magento\\Framework\\Controller\\Result\\JsonFactory $jsonFactory'],
			body="""parent::__construct($context);\n$this->jsonFactory = $jsonFactory;"""))
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
					            /** @var \Magento\Cms\Model\Block $block */
					            $model = $this->_objectManager->create('{model_class}')->load($modelid);
					            try {{
					                $model->setData(array_merge($model->getData(), $postItems[$modelid]));
					                $model->save();
					            }} catch (\Exception $e) {{
					                $messages[] = "[{model_name} ID: {{$modelid}}]  {{$e->getMessage()}}";
					                $error = true;
					            }}
					        }}
					    }}
					}}

					return $resultJson->setData([
					    'messages' => $messages,
					    'error' => $error
					]);""".format(
						model_class = model_class.class_namespace,
						model_name = model_name.replace('_', ' ').title(),
					)))
		self.add_class(inline_edit_controller)

		# new Controller
		new_controller = Phpclass('Controller\\Adminhtml\\' + model_name.replace('_', '') + '\\NewAction', extends='\\' + link_controller.class_namespace, 
			attributes=['protected $resultForwardFactory;'])
		new_controller.add_method(Phpmethod('__construct',
			params=['\\Magento\\Backend\\App\\Action\\Context $context',
				'\\Magento\\Framework\\Registry $coreRegistry',
				'\\Magento\\Backend\\Model\\View\\Result\\ForwardFactory $resultForwardFactory'],
			body="""$this->resultForwardFactory = $resultForwardFactory;\nparent::__construct($context, $coreRegistry);"""))
		new_controller.add_method(Phpmethod('execute',
			body="""/** @var \Magento\Framework\Controller\Result\Forward $resultForward */
					$resultForward = $this->resultForwardFactory->create();
					return $resultForward->forward('edit');"""))
		self.add_class(new_controller)

		# Save Controller
		new_controller = Phpclass('Controller\\Adminhtml\\' + model_name.replace('_', '') + '\\Save', extends='\\Magento\\Backend\\App\\Action', 
			attributes=['protected $dataPersistor;'])
		new_controller.add_method(Phpmethod('__construct',
			params=['\\Magento\\Backend\\App\\Action\\Context $context',
				'\\Magento\\Framework\\Registry $coreRegistry',
				'\\Magento\\Framework\\App\\Request\\DataPersistorInterface $dataPersistor'],
			body="""$this->dataPersistor = $dataPersistor;\nparent::__construct($context, $coreRegistry);"""))
		new_controller.add_method(Phpmethod('execute',
			body="""/** @var \Magento\Backend\Model\View\Result\Redirect $resultRedirect */
					$resultRedirect = $this->resultRedirectFactory->create();
					$data = $this->getRequest()->getPostValue();
					if ($data) {{
					    $id = $this->getRequest()->getParam('{model_id}');

					    $model = $this->_objectManager->create('{model_class}')->load($id);
					    if (!$model->getId() && $id) {{
					        $this->messageManager->addError(__('This {model_name} no longer exists.'));
					        return $resultRedirect->setPath('*/*/');
					    }}
									
					    $model->setData($data);

					    try {{
					        $model->save();
					        $this->messageManager->addSuccess(__('You saved the {model_name}.'));
					        $this->dataPersistor->clear('{register_model}');

					        if ($this->getRequest()->getParam('back')) {{
					            return $resultRedirect->setPath('*/*/edit', ['{model_id}' => $model->getId()]);
					        }}
					        return $resultRedirect->setPath('*/*/');
					    }} catch (LocalizedException $e) {{
					        $this->messageManager->addError($e->getMessage());
					    }} catch (\Exception $e) {{
					        $this->messageManager->addException($e, __('Something went wrong while saving the {model_name}.'));
					    }}

					    $this->dataPersistor->set('{register_model}', $data);
					    return $resultRedirect->setPath('*/*/edit', ['{model_id}' => $this->getRequest()->getParam('{model_id}')]);
					}}
					return $resultRedirect->setPath('*/*/');""".format(
						model_id = model_id,
						model_class = model_class.class_namespace,
						model_name = model_name.replace('_', ' ').title(),
						register_model = register_model
					)))
		self.add_class(new_controller)

		# Add model provider
		data_provider = Phpclass('Model\\' + model_name.replace('_', '') + '\\DataProvider', extends='\\Magento\\Ui\\DataProvider\\AbstractDataProvider', 
			attributes=['protected $collection;', 'protected $dataPersistor;', 'protected $loadedData;'],
			dependencies=[collection_model_class.class_namespace + 'Factory', 'Magento\\Framework\\App\\Request\\DataPersistorInterface'])
		data_provider.add_method(Phpmethod('__construct',
			params=['$name',
				'$primaryFieldName',
				'$requestFieldName',
				'CollectionFactory $collectionFactory',
				'DataPersistorInterface $dataPersistor',
				'array $meta = []',
				'array $data = []'],
			body="""$this->collection = $collectionFactory->create();
					$this->dataPersistor = $dataPersistor;
					parent::__construct($name, $primaryFieldName, $requestFieldName, $meta, $data);"""))
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
					)))

		self.add_class(data_provider)

		# Add model actions
		actions = Phpclass('Ui\Component\Listing\Column\\' + model_name.replace('_', '') + 'Actions', extends='\\Magento\\Ui\\Component\\Listing\\Columns\Column', 
			attributes=[
				"const URL_PATH_EDIT = '{}/{}/edit';".format(frontname, model_name.replace('_', '').lower()), 
				"const URL_PATH_DELETE = '{}/{}/delete';".format(frontname, model_name.replace('_', '').lower()),
				"const URL_PATH_DETAILS = '{}/{}/details';".format(frontname, model_name.replace('_', '').lower()),
				'protected $urlBuilder;',
			])
		actions.add_method(Phpmethod('__construct',
			params=['\\Magento\\Framework\\View\\Element\\UiComponent\\ContextInterface $context',
				'\\Magento\\Framework\\View\\Element\\UiComponentFactory $uiComponentFactory',
				'\\Magento\\Framework\\UrlInterface $urlBuilder',
				'array $components = []',
				'array $data = []'],
			body="""$this->urlBuilder = $urlBuilder;\nparent::__construct($context, $uiComponentFactory, $components, $data);"""))
		actions.add_method(Phpmethod('prepareDataSource', params=['array $dataSource'],
			body="""if (isset($dataSource['data']['items'])) {{
					foreach ($dataSource['data']['items'] as & $item) {{
					    if (isset($item['{model_id}'])) {{
					        $item[$this->getData('name')] = [
					            'edit' => [
					                'href' => $this->urlBuilder->getUrl(
					                    static::URL_PATH_EDIT,
					                    [
					                        '{model_id}' => $item['{model_id}']
					                    ]
					                ),
					                'label' => __('Edit')
					            ],
					            'delete' => [
					                'href' => $this->urlBuilder->getUrl(
					                    static::URL_PATH_DELETE,
					                    [
					                        '{model_id}' => $item['{model_id}']
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
						model_id = model_id
					)))
		self.add_class(actions)

		# Edit layout
		self.add_xml('view/adminhtml/layout/{}_{}_edit.xml'.format(frontname, model_name.replace('_', '').lower()), 
			Xmlnode('page', attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:framework:View/Layout/etc/page_configuration.xsd"}, nodes=[
				Xmlnode('update', attributes={'handle': 'styles'}),
				Xmlnode('body', nodes=[
					Xmlnode('referenceContainer', attributes={'name': 'content'}, nodes=[
						Xmlnode('uiComponent', attributes={'name': '{}_form'.format(model_table)})	
					])
				])
			]))

		# New layout
		self.add_xml('view/adminhtml/layout/{}_{}_new.xml'.format(frontname, model_name.replace('_', '').lower()), 
			Xmlnode('page', attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:framework:View/Layout/etc/page_configuration.xsd"}, nodes=[
				Xmlnode('update', attributes={'handle': '{}_{}_edit'.format(frontname, model_name.lower())})
			]))

		# UI Component Form
		data_source = '{}_form_data_source'.format(model_name.lower())
		ui_form = Xmlnode('form', attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:module:Magento_Ui:etc/ui_configuration.xsd"}, nodes=[
			Xmlnode('argument', attributes={'name': 'data', 'xsi:type': 'array'}, nodes=[
				Xmlnode('item', attributes={'name': 'js_config', 'xsi:type': 'array'}, nodes=[
					Xmlnode('item', attributes={'name': 'provider', 'xsi:type': 'string'}, node_text='{}_form.{}'.format(model_table, data_source)),
					Xmlnode('item', attributes={'name': 'deps', 'xsi:type': 'string'}, node_text='{}_form.{}'.format(model_table, data_source)),
				]),
				Xmlnode('item', attributes={'name': 'label', 'xsi:type': 'string', 'translate': 'true'}, node_text='General Information'),
				Xmlnode('item', attributes={'name': 'config', 'xsi:type': 'array'}, nodes=[
					Xmlnode('item', attributes={'name': 'dataScope', 'xsi:type': 'string'}, node_text='data'),
					Xmlnode('item', attributes={'name': 'namespace', 'xsi:type': 'string'}, node_text='{}_form'.format(model_table)),
				]),
				Xmlnode('item', attributes={'name': 'template', 'xsi:type': 'string'}, node_text='templates/form/collapsible'),
				Xmlnode('item', attributes={'name': 'buttons', 'xsi:type': 'array'}, nodes=[
					Xmlnode('item', attributes={'name': 'back', 'xsi:type': 'string'}, node_text=back_button.class_namespace),
					Xmlnode('item', attributes={'name': 'delete', 'xsi:type': 'string'}, node_text=delete_button.class_namespace),
					Xmlnode('item', attributes={'name': 'save', 'xsi:type': 'string'}, node_text=save_button.class_namespace),
					Xmlnode('item', attributes={'name': 'save_and_continue', 'xsi:type': 'string'}, node_text=save_continue_button.class_namespace),
				]),
			]),
			Xmlnode('dataSource', attributes={'name': data_source}, nodes=[
				Xmlnode('argument', attributes={'name': 'dataProvider', 'xsi:type': 'configurableObject'}, nodes=[
					Xmlnode('argument', attributes={'name': 'class', 'xsi:type': 'string'}, node_text=data_provider.class_namespace),
					Xmlnode('argument', attributes={'name': 'name', 'xsi:type': 'string'}, node_text=data_source),
					Xmlnode('argument', attributes={'name': 'primaryFieldName', 'xsi:type': 'string'}, node_text=model_id),
					Xmlnode('argument', attributes={'name': 'requestFieldName', 'xsi:type': 'string'}, node_text=model_id),
					Xmlnode('argument', attributes={'name': 'data', 'xsi:type': 'array'}, nodes=[
						Xmlnode('item', attributes={'name': 'config', 'xsi:type': 'array'}, nodes=[
							Xmlnode('item', attributes={'name': 'submit_url', 'xsi:type': 'url', 'path': '*/*/save'}),
						]),
					]),
				]),
				Xmlnode('argument', attributes={'name': 'data', 'xsi:type': 'array'}, nodes=[
					Xmlnode('item', attributes={'name': 'js_config', 'xsi:type': 'array'}, nodes=[
						Xmlnode('item', attributes={'name': 'component', 'xsi:type': 'string'}, node_text='Magento_Ui/js/form/provider'),
					]),
				]),
			]),
			Xmlnode('fieldset', attributes={'name': 'General'}, nodes=[
				Xmlnode('argument', attributes={'name': 'data', 'xsi:type': 'array'}, nodes=[
					Xmlnode('item', attributes={'name': 'config', 'xsi:type': 'array'}, nodes=[
						Xmlnode('item', attributes={'name': 'label', 'xsi:type': 'string'}),
					]),
				]),
				Xmlnode('field', attributes={'name': field_name}, nodes=[
					Xmlnode('argument', attributes={'name': 'data', 'xsi:type': 'array'}, nodes=[
						Xmlnode('item', attributes={'name': 'config', 'xsi:type': 'array'}, nodes=[
							Xmlnode('item', attributes={'name': 'dataType', 'xsi:type': 'string'}, node_text='text'),
							Xmlnode('item', attributes={'name': 'label', 'xsi:type': 'string', 'translate': 'true'}, node_text=field_name),
							Xmlnode('item', attributes={'name': 'formElement', 'xsi:type': 'string'}, node_text=field_element_type),
							Xmlnode('item', attributes={'name': 'source', 'xsi:type': 'string'}, node_text=model_name),
							Xmlnode('item', attributes={'name': 'sortOrder', 'xsi:type': 'number'}, node_text=str(10 * self.count)),
							Xmlnode('item', attributes={'name': 'dataScope', 'xsi:type': 'string'}, node_text=field_name),
							Xmlnode('item', attributes={'name': 'validation', 'xsi:type': 'array'}, nodes=[
								Xmlnode('item', attributes={'name': 'required-entry', 'xsi:type': 'boolean'}, node_text= 'true' if required else 'false'),
							]),
						]),
					]),
				]),
			]),
		])

		self.add_xml('view/adminhtml/ui_component/{}_form.xml'.format(model_table), ui_form)

		# Update UI Component index
		ui_index = Xmlnode('listing', attributes={'xsi:noNamespaceSchemaLocation': "urn:magento:module:Magento_Ui:etc/ui_configuration.xsd"}, nodes=[
			Xmlnode('argument', attributes={'name': 'data', 'xsi:type': 'array'}, nodes=[
				Xmlnode('item', attributes={'name': 'buttons', 'xsi:type': 'array'}, nodes=[
					Xmlnode('item', attributes={'name': 'add', 'xsi:type': 'array'}, nodes=[
						Xmlnode('item', attributes={'name': 'name', 'xsi:type': 'string'}, node_text='add'),
						Xmlnode('item', attributes={'name': 'label', 'xsi:type': 'string'}, node_text='Add new {}'.format(model_name)),
						Xmlnode('item', attributes={'name': 'class', 'xsi:type': 'string'}, node_text='primary'),
						Xmlnode('item', attributes={'name': 'url', 'xsi:type': 'string'}, node_text='*/*/new'),
					]),
				]),
			]),
			Xmlnode('columns', attributes={'name': '{}_columns'.format(model_table)}, nodes=[
				Xmlnode('argument', attributes={'name': 'data', 'xsi:type': 'array'}, nodes=[
					Xmlnode('item', attributes={'name': 'config', 'xsi:type': 'array'}, nodes=[
						Xmlnode('item', attributes={'name': 'editorConfig', 'xsi:type': 'array'}, nodes=[
							Xmlnode('item', attributes={'name': 'selectProvider', 'xsi:type': 'string'}, node_text='{0}_index.{0}_index.{0}_columns.ids'.format(model_table)),
							Xmlnode('item', attributes={'name': 'enabled', 'xsi:type': 'boolean'}, node_text='true'),
							Xmlnode('item', attributes={'name': 'indexField', 'xsi:type': 'string'}, node_text=model_id),
							Xmlnode('item', attributes={'name': 'clientConfig', 'xsi:type': 'array'}, nodes=[
								Xmlnode('item', attributes={'name': 'saveUrl', 'xsi:type': 'url', 'path': '{}/{}/inlineEdit'.format(frontname, model_name.replace('_', ''))}),
								Xmlnode('item', attributes={'name': 'validateBeforeSave', 'xsi:type': 'boolean'}, node_text='false'),
							]),
						]),
						Xmlnode('item', attributes={'name': 'childDefaults', 'xsi:type': 'array'}, nodes=[
							Xmlnode('item', attributes={'name': 'fieldAction', 'xsi:type': 'array'}, nodes=[
								Xmlnode('item', attributes={'name': 'provider', 'xsi:type': 'string'}, node_text='{0}_index.{0}_index.{0}_columns_editor'.format(model_table)),
								Xmlnode('item', attributes={'name': 'target', 'xsi:type': 'string'}, node_text='startEdit'),
								Xmlnode('item', attributes={'name': 'params', 'xsi:type': 'array'}, nodes=[
									Xmlnode('item', attributes={'name': '0', 'xsi:type': 'string'}, node_text='${ $.$data.rowIndex }'),
									Xmlnode('item', attributes={'name': '1', 'xsi:type': 'boolean'}, node_text='true'),
								]),
							]),
						]),
					]),
				]),
				Xmlnode('column', attributes={'name': field_name}, nodes=[
					Xmlnode('argument', attributes={'name': 'data', 'xsi:type': 'array'}, nodes=[
						Xmlnode('item', attributes={'name': 'config', 'xsi:type': 'array'}, nodes=[
							Xmlnode('item', attributes={'name': 'editor', 'xsi:type': 'array'}, nodes=[
								Xmlnode('item', attributes={'name': 'editorType', 'xsi:type': 'string'}, node_text=field_element_type if field_element_type == 'date' else 'text'),
								Xmlnode('item', attributes={'name': 'validation', 'xsi:type': 'array'}, nodes=[
									Xmlnode('item', attributes={'name': 'required-entry', 'xsi:type': 'boolean'}, node_text='true' if required else 'false'),
								]),
							]),
						]),
					]),
				]),
				Xmlnode('actionsColumn', attributes={'name': 'actions', 'class': actions.class_namespace}, nodes=[
					Xmlnode('argument', attributes={'name': 'data', 'xsi:type': 'array'}, nodes=[
						Xmlnode('item', attributes={'name': 'config', 'xsi:type': 'array'}, nodes=[
							Xmlnode('item', attributes={'name': 'indexField', 'xsi:type': 'string'}, node_text=model_id),
						]),
					]),
				]),
			]),
		])

		self.add_xml('view/adminhtml/ui_component/{}_index.xml'.format(model_table), ui_index)

	@classmethod
	def params(cls):
		return [
			SnippetParam(
				name='model_name', 
				required=True, 
				regex_validator= r'^[a-zA-Z]{1}\w+$',
				error_message='Only alphanumeric and underscore characters are allowed, and need to start with a alphabetic character.',
				repeat=True
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
			SnippetParam(name='adminhtml_form', yes_no=True),
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


