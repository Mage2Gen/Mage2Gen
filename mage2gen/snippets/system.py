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
import os
from .. import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam

class SystemSnippet(Snippet):
	snippet_label = 'System / Config / Setting'
	
	description = """
	System config is used in Magento for storing settings to use in your module.

	For example an option to enable and disable your module. 

	Generated configuration can be found in Magento Adminpanel > Stores > Settings > Configuration

	To retrieve the value you can use the xml path yourmodulename/general/enabled

	Example:
	--------
	.. code::

		$this->_scopeConfig->getValue('yourmodulename/general/enabled', \Magento\Store\Model\ScopeInterface::SCOPE_STORE);

	(Depends on \Magento\Framework\App\Config\ScopeConfigInterface)

	Field Types:
	------------
	- Select
	- Multiselect
	- Text
	- Textarea
	- Encrypted (Obscure)

	For Select and Multiselect you will need to define a source model. By default this will be this will be the core Magento yes/no.
	"""

	TYPE_CHOISES = [
		('text', 'Text'),
		('textarea', 'Textarea'),
		('select', 'Select'),
		('multiselect', 'Multiselect'),
		('obscure', 'Encrypted (Obscure)'),
	]

	SOURCE_MODELS = [
		('Magento\\Config\\Model\\Config\\Source\\Yesno','Yes/No'),
		('Magento\\Config\\Model\\Config\\Source\\Enabledisable','Enable/Disable'),
		('Magento\\Config\\Model\\Config\\Source\\Locale','Locale'),
		('Magento\\Config\\Model\\Config\\Source\\Store','Stores'),
		('Magento\\Config\\Model\\Config\\Source\\Website','Websites'),
		('Magento\\Config\\Model\\Config\\Source\\Nooptreq','No/Optional/Required'),
		('Magento\\Config\\Model\\Config\\Source\\Email\\Template','Email Template'),
		('Magento\\Config\\Model\\Config\\Source\\Email\\Identity','Email Identity'),
		('Magento\\Config\\Model\\Config\\Locale\\Source\\Currency','Currency'),
		('Magento\\Directory\\Model\\Config\\Source\\Country','Countries'),
		('Magento\\Payment\\Model\\Config\\Source\\Allspecificcountries','Payment | All Specific Countries'),
		('Magento\\Sales\\Model\\Config\\Source\\Order\\Status\\NewStatus','Sales | Order Status (state New)'),
		('Magento\\Sales\\Model\\Config\\Source\\Order\\Status\\Processing','Sales | Order Status (state Processing)'),
		('Magento\\Sales\\Model\\Config\\Source\\Order\\Status\\Newprocessing','Sales | Order Status (state New / Processing)'),
		('Magento\\Catalog\\Model\\Category\\Attribute\\Source\\Mode','Category | Display mode'),
		('Magento\\Catalog\\Model\\Category\\Attribute\\Source\\Page','Category | Static Block List'),
		('Magento\\Catalog\\Model\\Category\\Attribute\\Source\\Layout','Category | Page Layout'),
		('Magento\\Catalog\\Model\\Category\\Attribute\\Source\\Sortby','Category | Sort By'),
		('Magento\\Catalog\\Model\\Product\\Attribute\\Source\\Layout','Product | Layout'),
		('Magento\\Catalog\\Model\\Product\\Attribute\\Source\\Status','Product | Status'),
		('Magento\\Catalog\\Model\\Product\\Attribute\\Source\\Countryofmanufacture','Product | Country of manufacture'),
		('Magento\\Catalog\\Model\\Product\\Type','Product | Product Type'),
		('Magento\\Customer\\Model\\Customer\\Attribute\\Source\\Group','Customer | Group'),
		('Magento\\Customer\\Model\\Customer\\Attribute\\Source\\Store','Customer | Store'),
		('Magento\\Customer\\Model\\Customer\\Attribute\\Source\\Website','Customer | Website'),
		('','------------------'),
		('custom','Create Your own')
	]

	def add(self, tab, section, group, field, field_type='text', new_tab=False, extra_params=None, source_model=False, source_model_options=False):
		resource_id = self.module_name+'::config_'+self.module_name.lower()
		extra_params = extra_params if extra_params else {}

		tab_code = tab.lower().replace(' ', '_')
		section_code = section.lower().replace(' ', '_')
		group_code = group.lower().replace(' ', '_')
		field_code = field.lower().replace(' ', '_')

		# customer source model
		if source_model == 'custom' and source_model_options and field_type == 'select' or field_type == 'multiselect':

			source_model_class = Phpclass(
				'Model\\Config\\Source\\'+ ''.join(f.capitalize() for f in field_code.split('_')),
				implements=['\Magento\Framework\Option\ArrayInterface']
			)
			source_model_options = source_model_options.split(',')
			to_option_array = "[{}]".format(','.join("['value' => '{0}', 'label' => __('{0}')]".format(o.strip()) for o in source_model_options))
			to_array = "[{}]".format(','.join("'{0}' => __('{0}')".format(o.strip()) for o in source_model_options))

			source_model_class.add_method(Phpmethod('toOptionArray',body="return {};".format(to_option_array)))
			source_model_class.add_method(Phpmethod('toArray',body="return {};".format(to_array)))

			self.add_class(source_model_class)

			source_model = source_model_class.class_namespace


		# system xml
		file = 'etc/adminhtml/system.xml'	

		if new_tab :
			tabxml = Xmlnode('tab',attributes={
					'id':tab,
					'translate':'label',
					'sortOrder':extra_params.get('tab_sortOrder',999) or 999},nodes=[
				Xmlnode('label',node_text=extra_params.get('tab_label',tab) or tab)	
			 ])
		else:
			tabxml = False

		if field_type =='select' or field_type == 'multiselect' :
			source_model_xml = Xmlnode('source_model',node_text=source_model)
		else:
			source_model_xml = False



		if extra_params.get('field_backend_model'):
			backend_model_xml = Xmlnode('backend_model',node_text=extra_params.get('field_backend_model'))
		else:
			backend_model_xml = False

		if field_type == 'obscure' :
			backend_model_xml = Xmlnode('backend_model',node_text='Magento\\Config\\Model\\Config\\Backend\\Encrypted')
			config_path_xml = Xmlnode('config_path',node_text='{}/{}/{}'.format(section, group, field))
		else:
			config_path_xml = False


		label = extra_params.get('field_label',field) or field

		config = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Config:etc/system_file.xsd"}, nodes=[
				Xmlnode('system',  nodes=[
					tabxml,
					Xmlnode('section',attributes={
							'id':section,
							'sortOrder': extra_params.get('section_sortorder',10) or 10,
							'showInWebsite':1 if extra_params.get('section_show_in_website',True) else 0,
							'showInStore':1 if extra_params.get('section_show_in_store',True) else 0,
							'showInDefault': 1 if extra_params.get('section_show_in_default',True) else 0,
							'translate':'label'},match_attributes={'id'},nodes=[
						Xmlnode('label',node_text=extra_params.get('section_label',section) or section),
						Xmlnode('tab',node_text=tab),
						Xmlnode('resource',node_text=resource_id),
						Xmlnode('group', attributes={
								'id':group,'sortOrder':extra_params.get('group_sortorder',10) or 10,
								'showInWebsite': 1 if extra_params.get('group_show_in_website',True) else 0,
								'showInStore': 1 if extra_params.get('group_show_in_store',True) else 0,
								'showInDefault': 1 if extra_params.get('group_show_in_default',True) else 0,
								'translate':'label'},match_attributes={'id'},nodes=[
							Xmlnode('label',node_text=extra_params.get('group_label',group) or group),
							Xmlnode('field', attributes={
									'id':field,
									'type':field_type,
									'sortOrder':extra_params.get('field_sortorder',10) or 10,
									'showInWebsite': 1 if extra_params.get('field_show_in_website',True) else 0,
									'showInStore': 1 if extra_params.get('field_show_in_store',True) else 0,
									'showInDefault': 1 if extra_params.get('field_show_in_default',True) else 0,
									'translate':'label'},match_attributes={'id'},nodes=[
								Xmlnode('label',node_text=label),
								Xmlnode('comment',node_text=extra_params.get('field_comment')),
								source_model_xml,
								backend_model_xml,
								config_path_xml
							])
						])	
					])
				])
		])
		
		self.add_xml(file, config)


		if source_model == 'Magento\\Config\\Model\\Config\\Source\\Email\\Template':
			# email_templates xml
			email_templates_file = 'etc/email_templates.xml'
			email_template = '{}.html'.format(field_code)

			email_template_identifier = '{}_{}_{}'.format(section_code, group_code, field_code)
			email_template_config_identifier = '{}/{}/{}'.format(section_code, group_code, field_code)
			email_templates = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Email:etc/email_templates.xsd"}, nodes=[
				Xmlnode('template',attributes={'id': email_template_identifier,'label': label, 'file': email_template, 'type':'html', 'module': self.module_name, 'area':'frontend'},match_attributes={'id'})
			]);

			self.add_xml(email_templates_file, email_templates)
			self.add_static_file('view/frontend/email/', StaticFile(email_template, template_file='email.tmpl', context_data={'subject': label}))

			mail_helper = Phpclass(
				'Helper\\Mail',
				extends='AbstractHelper',
				dependencies=[
					'Magento\Framework\App\Helper\AbstractHelper',
					'Magento\Store\Model\ScopeInterface',
					'Magento\Framework\Exception\LocalizedException'
				],
				attributes=[
					'protected $transportBuilder;',
					'protected $storeManager;'
				]
			)

			mail_helper.add_method(
				Phpmethod(
					'__construct',
					params=[
						'\\Magento\\Framework\\App\\Helper\\Context $context',
						'\\Magento\\Framework\\Mail\\Template\\TransportBuilder $transportBuilder',
						'\\Magento\\Store\Model\\StoreManagerInterface $storeManager'
					],
					body="""
							$this->transportBuilder = $transportBuilder;
							$this->storeManager = $storeManager;
							parent::__construct($context);
					""",
					docstring=[
						'@param \Magento\Framework\App\Helper\Context $context',
						'@param \Magento\Framework\Mail\Template\TransportBuilder $transportBuilder'
						'@param \Magento\Store\Model\StoreManagerInterface $storeManager'
					]
				)
			)

			mail_helper.add_method(
				Phpmethod(
					'sendEmailTemplate',
					params=[
						'$template',
						'$sender',
						'$to = []',
						'$templateParams = []',
						'$storeId = null'
					],
					body="""
						if (!isset($to['email']) || empty($to['email'])) {
						    throw new LocalizedException(
						        __('We could not send the email because the receiver data is invalid.')
						    );
						}
						$storeId = $storeId ? $storeId : $this->storeManager->getStore()->getId();
						$name = isset($to['name']) ? $to['name'] : '';
						
						/** @var \Magento\Framework\Mail\TransportInterface $transport */
						$transport = $this->transportBuilder->setTemplateIdentifier(
						    $this->scopeConfig->getValue($template, ScopeInterface::SCOPE_STORE, $storeId)
						)->setTemplateOptions(
						    ['area' => \Magento\Framework\App\Area::AREA_FRONTEND, 'store' => $storeId]
						)->setTemplateVars(
						    $templateParams
						)->setScopeId(
						    $storeId
						)->setFrom(
						    $this->scopeConfig->getValue($sender, ScopeInterface::SCOPE_STORE, $storeId)
						)->addTo(
						    $to['email'],
						    $name
						)->getTransport();
						$transport->sendMessage();
					""",
					docstring=[
						'@param string $template configuration path of email template',
						'@param string $sender configuration path of email identity',
						'@param array $to email and name of the receiver',
						'@param array $templateParams',
						'@param int|null $storeId',
						'@throws \\Magento\\Framework\\Exception\\MailException',
						'@throws \\Magento\\Framework\\Exception\\NoSuchEntityException'
					],
					access='protected'
				)
			)

			email_name = ''.join(f.capitalize() for f in field_code.split('_'))
			mail_helper.add_method(
				Phpmethod(
					'send{}Email'.format(email_name),
					params=[
						'$sender = \'example@example.com\'',
						'$to = [\'email\' => \'\', \'name\' => \'\']'
					],
					body="""
						$this->sendEmailTemplate(
						    '{}',
						    $sender,
						    $to
						);
					""".format(email_template_config_identifier),
					docstring=[
						'Send the {} Email'.format(email_name)
					]
				)
			)
			self.add_class(mail_helper)

		# acl xml
		aclfile = 'etc/acl.xml'
		
		acl = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:framework:Acl/etc/acl.xsd"}, nodes=[
			Xmlnode('acl',nodes=[
				Xmlnode('resources',nodes=[
					Xmlnode('resource',attributes={'id':'Magento_Backend::admin'},match_attributes={'id'},nodes=[
						Xmlnode('resource',attributes={'id':'Magento_Backend::stores'},nodes=[
							Xmlnode('resource',attributes={'id':'Magento_Backend::stores_settings'},match_attributes={'id'},nodes=[
								Xmlnode('resource',attributes={'id':'Magento_Config::config'},match_attributes={'id'},nodes=[
									Xmlnode('resource',attributes={'id':resource_id,'title':section},match_attributes={'id'})
								])
							])
						])
					])
				])
			])
		]);

		self.add_xml(aclfile, acl)

		# default config values xml
		config_file = 'etc/config.xml'
		
		default_config = Xmlnode('config',attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Store:etc/config.xsd"},nodes=[
			Xmlnode('default',nodes=[
				Xmlnode(section,nodes=[
					Xmlnode(group,nodes=[
						Xmlnode(field,node_text=extra_params.get('field_default'))
					])
				])
			])
		]);
		
		self.add_xml(config_file, default_config)

	@classmethod
	def params(cls):
		return [
			SnippetParam(
				name='tab', 
				required=True, 
				description='Example: catalog',
				regex_validator= r'^[a-z]{1}[a-z0-9_]+$',
				error_message='Only lowercase alphanumeric and underscore characters are allowed, and need to start with a alphabetic character.',
				repeat=True),
			SnippetParam(
				name='new_tab', 
				default=True,
				yes_no=True,
				repeat=True),
			SnippetParam(
				name='section', 
				required=True, 
				description='Example: inventory',
				regex_validator= r'^[a-z]{1}[a-z0-9_]+$',
				error_message='Only lowercase alphanumeric and underscore characters are allowed, and need to start with a alphabetic character.',
				repeat=True),
			SnippetParam(
				name='group', 
				required=True, 
				description='Example: options',
				regex_validator= r'^[a-z]{1}[a-z0-9_]+$',
				error_message='Only lowercase alphanumeric and underscore characters are allowed, and need to start with a alphabetic character.',
				repeat=True),
			SnippetParam(
				name='field', 
				required=True, 
				description='Example: out of stock label ',
				regex_validator= r'^[a-z]{1}[a-z0-9_]+$',
				error_message='Only lowercase alphanumeric and underscore characters are allowed, and need to start with a alphabetic character.'),
			SnippetParam(
				name='field_type', 
				choises=cls.TYPE_CHOISES, 
				default='text'),
			SnippetParam(
				name='source_model', 
				choises=cls.SOURCE_MODELS,
				depend= {'field_type': r'select|multiselect'}, 
				default='Magento\Config\Model\Config\Source\Yesno'),
			SnippetParam(
				name='source_model_options',
				required=True,
				depend= {'source_model': r'custom'},
				description='comma seperated options. Example: yes,no.maybe',
				error_message='Only alphanumeric')

		]

	@classmethod
	def extra_params(cls):
		return [
			'Tab',
			SnippetParam(name='tab_label', repeat=True, description='Default uses tab value'),
			SnippetParam(
				name='tab_sortOrder',
				description='999',
				regex_validator= r'^\d+$',
				error_message='Only numeric value',
				repeat=True),
			'Section',
			SnippetParam(name='section_label', repeat=True, description='Default uses section value'),
			SnippetParam(
				name='section_sortorder',
				description='10',
				regex_validator= r'^\d+$',
				error_message='Only numeric value',
				repeat=True),
			SnippetParam(
				name='section_show_in_website',
				default=True,
				yes_no=True,
				repeat=True),
			SnippetParam(
				name='section_show_in_store',
				default=True,
				yes_no=True,
				repeat=True),
			SnippetParam(
				name='section_show_in_default',
				default=True,
				yes_no=True,
				repeat=True),
			'Group',
			SnippetParam(name='group_label', repeat=True, description='Default uses group value'),
			SnippetParam(
				name='group_sortorder',
				description='10',
				regex_validator= r'^\d+$',
				error_message='Only numeric value',
				repeat=True),
			SnippetParam(
				name='group_show_in_website',
				default=True,
				yes_no=True,
				repeat=True),
			SnippetParam(
				name='group_show_in_store',
				default=True,
				yes_no=True,
				repeat=True),
			SnippetParam(
				name='group_show_in_default',
				default=True,
				yes_no=True,
				repeat=True),
			'Field',
			SnippetParam(name='field_label', description='Default uses field value'),
			SnippetParam(name='field_comment', description='Example: Label used to display out of stock status'),
			SnippetParam(name='field_default', description='Default value of field'),
			SnippetParam(
				name='field_sortorder',
				description='10',
				regex_validator= r'^\d+$',
				error_message='Only numeric value'),
			SnippetParam(
				name='field_show_in_website',
				default=True,
				yes_no=True),
			SnippetParam(
				name='field_show_in_store',
				default=True,
				yes_no=True),
			SnippetParam(
				name='field_show_in_default',
				default=True,
				yes_no=True),
			SnippetParam(
				name='field_backend_model',
				regex_validator=r'^[\w\\]+$',
				error_message='Only alphanumeric, underscore and backslash characters are allowed'),
		]
