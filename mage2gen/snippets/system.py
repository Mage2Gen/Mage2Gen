import os
from mage2gen import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet

class SystemSnippet(Snippet):

	def add(self, section, group, field, label, type, comment):

		file = 'etc/adminhtml/system.xml'	

		config = Xmlnode('config', attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Config:etc/system_file.xsd"}, nodes=[
				Xmlnode('system',  nodes=[
					Xmlnode('section',attributes={'id':section},match_attributes={'id'},nodes=[
						Xmlnode('group', attributes={'id':group},match_attributes={'id'},nodes=[
							Xmlnode('field', attributes={'id':field},match_attributes={'id'},nodes=[
								Xmlnode('label',match_attributes={'id'},node_text=label),
								Xmlnode('source_model',match_attributes={'id'},node_text='test3')
							])
						])	
					])
				])
		])

		self.add_xml(file, config)

		aclfile = 'etc/acl.xml'