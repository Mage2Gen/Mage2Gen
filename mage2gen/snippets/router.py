import os
from .. import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam, Readme

class RouterSnippet(Snippet):
	snippet_label = "Router"

	description = """
	Custom routers
	
	Create an implementation of RouterInterface to create a custom router, and define the match() function in this class to use your own route matching logic.

	If you need route configuration data, use the Route Config class.
	"""


	def add(self, routername='', adminhtml=False, ajax=False, extra_params=None, top_level_menu=True):
		file = 'etc/{}/di.xml'.format('adminhtml' if adminhtml else 'frontend')
		# create route class
		router_class = ['Controller']
		if adminhtml:
			router_class.append('Adminhtml')
		router_class.append('Router')

		router = Phpclass('\\'.join(router_class), implements=["RouterInterface"], dependencies=[
			'Magento\\Framework\\App\\Action\\Forward',
			'Magento\\Framework\\App\\ActionFactory',
			'Magento\\Framework\\App\\RequestInterface',
			'Magento\\Framework\\App\\RouterInterface',
		], attributes=[
			'protected $transportBuilder;',
			'protected $actionFactory;'
		])

		router.add_method(Phpmethod(
			'__construct',
			body="$this->actionFactory = $actionFactory;",
			params=[
				"ActionFactory $actionFactory"
			],
			docstring=[
				'Router constructor',
				'',
				'@param ActionFactory $actionFactory',
			]
		))

		router.add_method(Phpmethod(
			'match',
			body="""
		$result = null;

	if ($request->getModuleName() != 'example' && $this->validateRoute($request)) {
	    $request->setModuleName('example')
	        ->setControllerName('index')
	        ->setActionName('index')
	        ->setParam('param', 3);
	    $result = $this->actionFactory->create(Forward::class);
	}
	return $result;
			""",
			params=[
				"RequestInterface $request"
			],
			docstring=[
				'{@inheritdoc}',
			]
		))

		router.add_method(Phpmethod(
			'validateRoute',
			body="$identifier = trim($request->getPathInfo(), '/');\nreturn strpos($identifier, '{}') !== false;".format(routername),
			params=[
				"RequestInterface $request"
			],
			docstring=[
				'@param RequestInterface $request',
				'@return bool',
			]
		))
		self.add_class(router)



		# Create config router
		module = Xmlnode('module', attributes={'name': self.module_name})
		if adminhtml:
			module.attributes['before'] = 'Magento_Backend'

		router_list_config = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:framework:ObjectManager/etc/config.xsd"}, nodes=[
			Xmlnode('type', attributes={'name': 'Magento\Framework\App\RouterList'}, nodes=[
				Xmlnode('arguments', nodes=[
					Xmlnode('argument', attributes={'name': 'routerList', 'xsi:type': 'array'}, nodes=[
						Xmlnode('item', attributes={'name': '{}'.format(routername), 'xsi:type': 'array'}, nodes=[
							Xmlnode('item', attributes={'name': 'class', 'xsi:type': 'string'}, node_text=router.class_namespace),
							Xmlnode('item', attributes={'name': 'disable', 'xsi:type': 'boolean'}, node_text="false"),
							Xmlnode('item', attributes={'name': 'sortOrder', 'xsi:type': 'string'}, node_text="999"),
						])
					])
				])
			])
		])
		self.add_xml(file, router_list_config)

	@classmethod
	def params(cls):
		return [
			SnippetParam(name='routername', required=False, description='On empty uses module name in lower case',
				regex_validator= r'^[a-z]{1}\w+$',
				error_message='Only lowercase alphanumeric and underscore characters are allowed, and need to start with a alphabetic character.',
				repeat=True),
			SnippetParam(name='adminhtml', yes_no=True),
		]
