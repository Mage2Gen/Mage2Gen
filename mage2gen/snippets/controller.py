# A Magento 2 module generator library
# Copyright (C) 2016 Maikel Martens
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

class ControllerSnippet(Snippet):
	description = """
	Controller is used to serve a request path. A request path look like this:

		www.yourmagentoinstallation.com/frontname/section/action

	- **frontname:** Configured in the router.xml and must be unique.
	- **section:** Is a subfolder or folders to the action class.
	- **action:** An action class that will execute the reqeust.

	This snippet will also create a layout.xml, Block and phtml for the action.
	"""

	def add(self, frontname='', section='index', action='index', adminhtml=False):
		if not frontname:
			frontname = self._module.name.lower()
		file = 'etc/{}/routes.xml'.format('adminhtml' if adminhtml else 'frontend')

		# Create config router
		module = Xmlnode('module', attributes={'name': self.module_name})
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
				Xmlnode('referenceContainer', attributes={'name': 'content'}, nodes=[
					Xmlnode('block', attributes={
						'name': "{}.{}".format(section, action), 
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


	@classmethod
	def params(cls):
		return [
			SnippetParam(name='frontname', required=False, description='When empty it will use the Module name in lower case',
				regex_validator= r'^[a-zA-Z]{1}\w+$',
				error_message='Only alphanumeric and underscore characters are allowed, and need to start with a alphabetic character.'),
			SnippetParam(name='section', required=False, default='index',
				regex_validator= r'^[a-zA-Z]{1}\w+$',
				error_message='Only alphanumeric and underscore characters are allowed, and need to start with a alphabetic character.'),
			SnippetParam(name='action', required=False, default='index',
				regex_validator= r'^[a-zA-Z]{1}\w+$',
				error_message='Only alphanumeric and underscore characters are allowed, and need to start with a alphabetic character.'),
			SnippetParam(name='adminhtml', yes_no=True),
		]