import os
from mage2gen import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet

class PluginSnippet(Snippet):
	TYPE_BEFORE = 'before'
	TYPE_AFTER = 'after'
	TYPE_AROUND = 'around'

	def add(self, classname, methodname, plugintype=TYPE_AFTER, sortorder=10, disabled=False):
		# Add class
		plugin = Phpclass('Plugin\\{}'.format(classname))
		
		variable = '$result'
		if plugintype == self.TYPE_BEFORE:
			variable = '$functionvariables'
		elif plugintype == self.TYPE_AROUND:
			variable = '\Closure $proceed' 

		plugin.add_method(Phpmethod(
			plugintype + methodname[0].capitalize() + methodname[1:],
			params=[
				classname + ' $subject',
				variable
			]
		))
	
		# Add plug first will add the module namespace to PhpClass
		self.add_class(plugin)	

		# Plugin XML
		config = Xmlnode('config', attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:framework:ObjectManager/etc/config.xsd"}, nodes=[
			Xmlnode('type', attributes={'name': classname}, nodes=[
				Xmlnode('plugin', attributes={
					'name': plugin.class_namespace.replace('\\', '_'),
					'type':plugin.class_namespace,
					'sortOrder':sortorder,
					'disabled':'true' if disabled else 'false'
				})
			])
		])

		self.add_xml('etc/di.xml', config)
		
