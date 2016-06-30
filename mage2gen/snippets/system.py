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
from mage2gen import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam

class SystemSnippet(Snippet):
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

	For Select and Multiselect you will need to define a source model. By default this will be this will be the core Magento yes/no.
	"""

	TYPE_CHOISES = [
		('text', 'Text'),
		('textarea', 'Textarea'),
		('select', 'Select'),
		('multiselect', 'Multiselect'),
	]

	def add(self, tab, section, group, field, field_type='text', tab_options=None, section_options=None, group_options=None, field_options=None, new_tab=False):

		resource_id = self.module_name+'::config_'+self.module_name.lower()
		tab_options = tab_options if tab_options else {}
		section_options = section_options if section_options else {}
		group_options = group_options if group_options else {}
		field_options = field_options if field_options else {}

		tab_code = tab.lower().replace(' ', '_')
		section_code = section.lower().replace(' ', '_')
		group_code = group.lower().replace(' ', '_')
		field_code = field.lower().replace(' ', '_')

		file = 'etc/adminhtml/system.xml'	

		if new_tab :
			tabxml = Xmlnode('tab',attributes={'id':tab,'translate':tab_options.get('translate','label'),'sortOrder':tab_options.get('sortOrder',999)},nodes=[
						Xmlnode('label',node_text=tab_options.get('label',tab))	
					 ])
		else:
			tabxml = False

		if field_type =='select' or field_type == 'multiselect' :
			source_model_xml = Xmlnode('source_model',node_text='Magento\Config\Model\Config\Source\Yesno')
		else:
			source_model_xml = False

		if field_options.get('backend_model'):
			backend_model_xml = Xmlnode('backend_model',node_text=field_options.get('backend_model'))
		else:
			backend_model_xml = False			

		config = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Config:etc/system_file.xsd"}, nodes=[
				Xmlnode('system',  nodes=[
					tabxml,
					Xmlnode('section',attributes={'id':section,'sortOrder':section_options.get('sortorder',10),'showInWebsite':section_options.get('show_in_website',1),'showInStore':section_options.get('show_in_store',1),'showInDefault':section_options.get('show_in_default',1),'translate':'label'},match_attributes={'id'},nodes=[
						Xmlnode('label',node_text=section_options.get('label',section)),
						Xmlnode('tab',node_text=tab),
						Xmlnode('resource',node_text=resource_id),
						Xmlnode('group', attributes={'id':group,'sortOrder':group_options.get('sortorder',10),'showInWebsite':group_options.get('show_in_website',1),'showInStore':group_options.get('show_in_store',1),'showInDefault':group_options.get('show_in_default',1),'translate':'label'},match_attributes={'id'},nodes=[
							Xmlnode('field', attributes={'id':field,'type':field_type,'sortOrder':field_options.get('sortorder',10),'showInWebsite':field_options.get('show_in_website',1),'showInStore':field_options.get('show_in_store',1),'showInDefault':field_options.get('show_in_default',1),'translate':'label'},match_attributes={'id'},nodes=[
								Xmlnode('label',node_text=field_options.get('label',field)),
								Xmlnode('comment',node_text=field_options.get('comment')),
								source_model_xml,
								backend_model_xml
							])
						])	
					])
				])
		])

		self.add_xml(file, config)

		aclfile = 'etc/acl.xml'
		
		acl = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:framework:Acl/etc/acl.xsd"}, nodes=[
			Xmlnode('acl',nodes=[
				Xmlnode('resources',nodes=[
					Xmlnode('resource',attributes={'id':'Magento_Backend::admin'},match_attributes={'id'},nodes=[
						Xmlnode('resource',attributes={'id':'Magento_Backend::stores'},nodes=[
							Xmlnode('resource',attributes={'id':'Magento_Backend::stores_settings'},match_attributes={'id'},nodes=[
								Xmlnode('resource',attributes={'id':'Magento_Config::config'},match_attributes={'id'},nodes=[
									Xmlnode('resource',attributes={'id':resource_id},match_attributes={'id'})
								])
							])
						])
					])
				])
			])
		]);

		self.add_xml(aclfile, acl)

		config_file = 'etc/config.xml'
		
		default_config = Xmlnode('config',attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Store:etc/config.xsd"},nodes=[
			Xmlnode('default',nodes=[
				Xmlnode(section,nodes=[
					Xmlnode(group,nodes=[
						Xmlnode(field,node_text=field_options.get('default'))
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
				description='Tab code. Example: catalog',
				regex_validator= r'^[a-z\d\-_\s]+$',
				error_message='Only alphanumeric'),
			SnippetParam(
				name='new_tab', 
				default=True,
				yes_no=True),
			SnippetParam(
				name='section', 
				required=True, 
				description='Section code. Example: inventory',
				regex_validator= r'^[a-z\d\-_\s]+$',
				error_message='Only alphanumeric'),
			SnippetParam(
				name='group', 
				required=True, 
				description='Group code. Example: options',
				regex_validator= r'^[a-z\d\-_\s]+$',
				error_message='Only alphanumeric'),
			SnippetParam(
				name='field', 
				required=True, 
				description='Field code. Example: out of stock label ',
				regex_validator= r'^[a-z\d\-_\s]+$',
				error_message='Only alphanumeric'),
			SnippetParam(
				name='field_type', 
				choises=cls.TYPE_CHOISES, 
				default='text'),
		]