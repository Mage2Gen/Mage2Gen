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

	def add(self, tab, section, group, field, field_type='text', new_tab=False, extra_params=None):
		resource_id = self.module_name+'::config_'+self.module_name.lower()
		extra_params = extra_params if extra_params else {}

		tab_code = tab.lower().replace(' ', '_')
		section_code = section.lower().replace(' ', '_')
		group_code = group.lower().replace(' ', '_')
		field_code = field.lower().replace(' ', '_')

		file = 'etc/adminhtml/system.xml'	

		if new_tab :
			tabxml = Xmlnode('tab',attributes={
					'id':tab,
					'translate':'label',
					'sortOrder':extra_params.get('tab_sortOrder',999)},nodes=[
				Xmlnode('label',node_text=extra_params.get('tab_label',tab))	
			 ])
		else:
			tabxml = False

		if field_type =='select' or field_type == 'multiselect' :
			source_model_xml = Xmlnode('source_model',node_text='Magento\Config\Model\Config\Source\Yesno')
		else:
			source_model_xml = False

		if extra_params.get('field_backend_model'):
			backend_model_xml = Xmlnode('backend_model',node_text=extra_params.get('field_backend_model'))
		else:
			backend_model_xml = False			

		config = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Config:etc/system_file.xsd"}, nodes=[
				Xmlnode('system',  nodes=[
					tabxml,
					Xmlnode('section',attributes={
							'id':section,
							'sortOrder':extra_params.get('section_sortorder',10),
							'showInWebsite':1 if extra_params.get('section_show_in_website',True) else 0,
							'showInStore':1 if extra_params.get('section_show_in_store',True) else 0,
							'showInDefault': 1 if extra_params.get('section_show_in_default',True) else 0,
							'translate':'label'},match_attributes={'id'},nodes=[
						Xmlnode('label',node_text=extra_params.get('section_label',section)),
						Xmlnode('tab',node_text=tab),
						Xmlnode('resource',node_text=resource_id),
						Xmlnode('group', attributes={
								'id':group,'sortOrder':extra_params.get('group_sortorder',10),
								'showInWebsite': 1 if extra_params.get('group_show_in_website',True) else 0,
								'showInStore': 1 if extra_params.get('group_show_in_store',True) else 0,
								'showInDefault': 1 if extra_params.get('group_show_in_default',True) else 0,
								'translate':'label'},match_attributes={'id'},nodes=[
							Xmlnode('field', attributes={
									'id':field,
									'type':field_type,
									'sortOrder':extra_params.get('field_sortorder',10),
									'showInWebsite': 1 if extra_params.get('field_show_in_website',True) else 0,
									'showInStore': 1 if extra_params.get('field_show_in_store',True) else 0,
									'showInDefault': 1 if extra_params.get('field_show_in_default',True) else 0,
									'translate':'label'},match_attributes={'id'},nodes=[
								Xmlnode('label',node_text=extra_params.get('field_label',field)),
								Xmlnode('comment',node_text=extra_params.get('field_comment')),
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

	@classmethod
	def extra_params(cls):
		return [
			'Tab',
			SnippetParam(
				name='tab_sortOrder',
				regex_validator= r'^\d+$',
				error_message='Only numeric value'),
			SnippetParam(name='tab_label'),
			'Section',
			SnippetParam(name='section_label'),
			SnippetParam(
				name='section_sortorder',
				regex_validator= r'^\d+$',
				error_message='Only numeric value'),
			SnippetParam(
				name='section_show_in_website',
				default=True,
				yes_no=True),
			SnippetParam(
				name='section_show_in_store',
				default=True,
				yes_no=True),
			SnippetParam(
				name='section_show_in_default',
				default=True,
				yes_no=True),
			'Group',
			SnippetParam(
				name='group_sortorder',
				regex_validator= r'^\d+$',
				error_message='Only numeric value'),
			SnippetParam(
				name='group_show_in_website',
				default=True,
				yes_no=True),
			SnippetParam(
				name='group_show_in_store',
				default=True,
				yes_no=True),
			SnippetParam(
				name='group_show_in_default',
				default=True,
				yes_no=True),
			'Field',
			SnippetParam(name='field_label'),
			SnippetParam(name='field_comment'),
			SnippetParam(name='field_default'),
			SnippetParam(
				name='field_sortorder',
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