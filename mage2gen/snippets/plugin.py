import os
from mage2gen import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet

class PluginSnippet(Snippet):

	def add(self, classname, sortorder, disabled):
		file = 'etc/di.xml'

		plugin_name = self.module_name.lower() + '_' + classname.lower().replace('\\','_')
		plugin_class = self.module_name.replace('_','\\') + '\\Plugin' + '\\' + classname
		
		config = Xmlnode('config', attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:framework:ObjectManager/etc/config.xsd"}, nodes=[
			Xmlnode('type', attributes={'name':classname}, nodes=[
				Xmlnode('plugin', attributes={'name': plugin_name,'type':plugin_class,'sortOrder':sortorder,'disabled':disabled})
			])
		])

		self.add_xml(file, config)
