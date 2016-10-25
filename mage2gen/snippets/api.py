import os, locale
from mage2gen import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam
from mage2gen.utils import upperfirst
from mage2gen.module import TEMPLATE_DIR

class InterfaceClass(Phpclass):

	template_file = os.path.join(TEMPLATE_DIR,'interface.tmpl')

class InterfaceMethod(Phpmethod):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.template_file = os.path.join(TEMPLATE_DIR,'interfacemethod.tmpl')

class ApiSnippet(Snippet):

	snippet_label = 'Api'

	description = """
		Create your own api. Test is with the build in api tester in your magento 2 installation. http://<yourmagento2website>/swagger 

		WARNING. This api is public. Acl will be added soon.
	"""
	API_METHOD_CHOISES = [
		('POST', 'POST'),
		('GET', 'GET'),
		('PUT', 'PUT'),
		('DELETE', 'DELETE'),
	]

	def add(self, api_name, api_method='GET',extra_params=None):

		methodname = api_name;
		url = '/V1/'+ self._module.package.lower() + '-' + self._module.name.lower()+'/'+api_name.lower();
		resource = 'anonymous';
		description = api_method + ' for ' + api_name + ' api'


		management_interface = InterfaceClass('Api\\' + methodname + 'ManagementInterface')
		management_interface.add_method(InterfaceMethod(api_method.lower() + upperfirst(api_name),params=['$param'],docstring=[description,'@param string $param','@return string']))

		self.add_class(management_interface)
		api_classname = management_interface.class_namespace


		model = Phpclass('\\'.join(['Model',methodname + 'Management']))
		model.add_method(Phpmethod(
			api_method.lower() + upperfirst(api_name),
			params=['$param'],
			docstring=['{@inheritdoc}'],
			body="return 'hello api " + api_method + " return the $param ' . $param;"
		))

		self.add_class(model)
		model_classname = model.class_namespace


		di_xml = Xmlnode('config', attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:framework:ObjectManager/etc/config.xsd"}, nodes=[
			Xmlnode('preference', attributes={'for': api_classname, 'type': model_classname})
		])

		self.add_xml('etc/di.xml', di_xml)

		webapi_xml = Xmlnode('routes', attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Webapi:etc/webapi.xsd"}, nodes=[
			Xmlnode('route', attributes={'url': url, 'method': api_method},match_attributes={'url','method'},nodes=[
				Xmlnode('service',attributes={'class':api_classname,'method':api_method.lower() + upperfirst(api_name)}),
				Xmlnode('resources',nodes=[
					Xmlnode('resource', attributes={'ref':resource})
				])
			])
		])

		self.add_xml('etc/webapi.xml', webapi_xml)

		##Apiclass

	@classmethod	
	def params(cls):
		return [
			SnippetParam(name='api_name', required=True,
				regex_validator= r'^\w+$',
				error_message='Only alphanumeric and underscore characters are allowed'),
			SnippetParam(name='api_method', choises=cls.API_METHOD_CHOISES, default='GET'),
		]

	@classmethod
	def extra_params(cls):
		return []	
