import os
from mage2gen import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet

class ControllerSnippet(Snippet):

	def add(self, frontname, section, action, adminhtml=False):
		file = 'etc/{}/routes.xml'.format('adminhtml' if adminhtml else 'frontend')

		# Create config router
		module = Xmlnode('module', self.module_name)
		if adminhtml:
			module.attributes['before'] = 'Magento_Backend'

		config = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:framework:App/etc/routes.xsd"}, nodes=[
			Xmlnode('router', attributes={'id': 'admin' if adminhtml else 'standard'}, nodes=[
				Xmlnode('route', attributes={'id': frontname, 'frontName': frontname}, nodes=[
					module
				])
			])
		])
		self.add_xml(file, config)

		# Create controller
		controller_class = ['Controller']
		if adminhtml:
			controller_class.append('Adminhtml')
		controller_class.append(section)
		controller_class.append(action)

		controller = Phpclass('\\'.join(controller_class), '\Magento\Framework\App\Action\Action')
		controller.attributes.append('protected $resultPageFactory;')
		controller.add_method(Phpmethod(
			'__construct',
			params=[
				'\Magento\Framework\App\Action\Context $context',
				'\Magento\Framework\View\Result\PageFactory $resultPageFactory'
			],
			body="""$this->resultPageFactory = $resultPageFactory;
				parent::__construct($context);
			"""
		))
		controller.add_method(Phpmethod(
			'execute',
			body='return $this->resultPageFactory->create();'
		))

		self.add_class(controller)

		# create block
		block_class = ['Block']
		if adminhtml:
			block_class.append('Adminhtml')
		block_class.append(section)
		block_class.append(action)

		block = Phpclass('\\'.join(block_class), '\Magento\Framework\View\Element\Template')
		self.add_class(block)

		# Add layout xml
		layout_xml = Xmlnode('page', attributes={'layout':"admin-1column" if adminhtml else "1column", 'xsi:noNamespaceSchemaLocation':"urn:magento:framework:View/Layout/etc/page_configuration.xsd"}, nodes=[
			Xmlnode('body', nodes=[
				Xmlnode('referenceContainer', 'content', nodes=[
					Xmlnode('block', "{}.{}".format(section, action), attributes={
						'class': block.class_namespace,
						'template': "{}::{}_{}.phtml".format(self.module_name, section, action)
					})
				])
			])
		])
		path = os.path.join('view', 'adminhtml' if adminhtml else 'frontend', 'layout', "{}_{}_{}.xml".format(frontname, section, action))
		self.add_xml(path, layout_xml)

		# add template file
		path = os.path.join('view', 'adminhtml' if adminhtml else 'frontend', 'templates')
		self.add_static_file(path, StaticFile('order_json.phtml'))