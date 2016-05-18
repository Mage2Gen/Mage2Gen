
class Snippet:

	def __init__(self, module):
		self._module = module

	@property
	def module_name(self):
	    return self._module.module_name

	def add_class(self, phpclass):
		return self._module.add_class(phpclass)

	def add_xml(self, xml_file, node):
		return self._module.add_xml(xml_file, node)

	def add_static_file(self, path, staticfile):
		return self._module.add_static_file(path, staticfile)

	def add(self, *args, **kwargs):
		raise Exception('Not implemented')