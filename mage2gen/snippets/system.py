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
from mage2gen import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet

class SystemSnippet(Snippet):

	def add(self, tab, section, group, field, section_options, group_options, field_options):

		file = 'etc/adminhtml/system.xml'	

		config = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Config:etc/system_file.xsd"}, nodes=[
				Xmlnode('system',  nodes=[
					Xmlnode('section',attributes={'id':section,'sortOrder':field_options.get('sortorder',10),'showInWebsite':field_options.get('show_in_website',1),'showInStore':field_options.get('show_in_store',1),'showInDefault':field_options.get('show_in_default',1),'translate':'label'},match_attributes={'id'},nodes=[
						Xmlnode('group', attributes={'id':group,'sortOrder':field_options.get('sortorder',10),'showInWebsite':field_options.get('show_in_website',1),'showInStore':field_options.get('show_in_store',1),'showInDefault':field_options.get('show_in_default',1),'translate':'label'},match_attributes={'id'},nodes=[
							Xmlnode('field', attributes={'id':field,'type':field_options.get('type','text'),'sortOrder':field_options.get('sortorder',10),'showInWebsite':field_options.get('show_in_website',1),'showInStore':field_options.get('show_in_store',1),'showInDefault':field_options.get('show_in_default',1),'translate':'label'},match_attributes={'id'},nodes=[
								Xmlnode('label',node_text=field_options.get('label','label')),
								Xmlnode('source_model',node_text=field_options.get('source_model')),
								Xmlnode('comment',node_text=field_options.get('comment'))
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
						Xmlnode('resource',attributes={'id':'Magento_Backend::stores_settings'},match_attributes={'id'},nodes=[
							Xmlnode('resource',attributes={'id':'Magento_Config::config'},match_attributes={'id'},nodes=[
								Xmlnode('resource',attributes={'id':'Experius_Core::experius_core'},match_attributes={'id'})
							])
						])
					])
				])
			])
		]);

		self.add_xml(aclfile, acl)

		config_file = 'etc/config.xml'
		
		default_config = Xmlnode('config',attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Store:etc/config.xsd"},nodes=[
			Xmlnode(section,nodes=[
				Xmlnode(group,nodes=[
					Xmlnode(field,node_text=field_options.get('default'))
				])
			])
		]);
		
		self.add_xml(config_file, default_config)