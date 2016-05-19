import os
from mage2gen import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet

class PluginSnippet(Snippet):

	def add(self, classname, sortorder=10, disabled='false', methodname='getName', plugintype='after'):
		file = 'etc/di.xml'

		plugin_name = self.module_name.lower() + '_' + classname.lower().replace('\\','_')
		plugin_class = self.module_name.replace('_','\\') + '\\Plugin' + '\\' + classname
		
		config = Xmlnode('config', attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:framework:ObjectManager/etc/config.xsd"}, nodes=[
			Xmlnode('type','classname', nodes=[
				Xmlnode('plugin', plugin_name, attributes={'type':plugin_class,'sortOrder':sortorder,'disabled':disabled})
			])
		])

		self.add_xml(file, config)

		plugin_class = ['Plugin']
		plugin_class.append(classname)

		plugin = Phpclass('\\'.join(plugin_class))	

		variable = '$result'

		if plugintype=='before':
			variable = '$functionvariables'
		elif plugintype=='around':
			variable = '\Closure $proceed' 

		plugin.add_method(Phpmethod(
			plugintype + methodname[0].capitalize() + methodname[1:],
			params=[
				classname + ' $subject',
				variable
			],
			body='//return;'
		))
		
		self.add_class(plugin)
