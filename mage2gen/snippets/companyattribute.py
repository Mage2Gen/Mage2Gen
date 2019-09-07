
# A Magento 2 module generator library
# Copyright (C) 2019 Mr. Lewis
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
from .. import Phpclass, Phpmethod, Xmlnode, Snippet, SnippetParam

class CompanyAttributeSnippet(Snippet):
	snippet_label = 'Company Attribute'

	FRONTEND_INPUT_TYPE = [
        ("input","Text Field"),
        ("textarea","Text Area"),
    ]

	description ="""
		With this snippet you can create company attribute programmatically through a Magento 2 InstallSchema or UpdateSchema setup script and adds the fields to the admin form.

		Magento 2 create company attribute programmatically
	"""

	def add(self,attribute_label, frontend_input='input', upgrade_data=False, from_version='1.0.1', required=False, extra_params=None):

		extra_params = extra_params if extra_params else {}
		attribute_code = extra_params.get('attribute_code', None)

		if not attribute_code:
			attribute_code = attribute_label.lower().replace(' ','_')[:30]

		templatePath = os.path.join(os.path.dirname(__file__), '../templates/attributes/companyattribute.tmpl')

		with open(templatePath, 'rb') as tmpl:
			template = tmpl.read().decode('utf-8')

		methodBody = template.format(
			attribute_code=attribute_code,
			attribute_label=attribute_label
		)

		setupType = 'Install'
		if upgrade_data:
			setupType = 'Upgrade'


		install_data = Phpclass(
			'Setup\\{}Schema'.format(setupType),
			implements=['{}SchemaInterface'.format(setupType)],
			dependencies=[
				'Magento\\Framework\\Setup\\{}SchemaInterface'.format(setupType),
				'Magento\\Framework\\Setup\\SchemaSetupInterface'.format(setupType),
				'Magento\\Framework\\Setup\\ModuleContextInterface',
				],
			attributes=[]
		)

		install_data.add_method(Phpmethod('{}'.format(setupType.lower()),
			params=['SchemaSetupInterface $setup'.format(setupType),'ModuleContextInterface $context'],
			body="",
			docstring=['{@inheritdoc}']))

		if upgrade_data:
			install_data.add_method(Phpmethod('{}'.format(setupType.lower()),
				params=['SchemaSetupInterface $setup'.format(setupType),'ModuleContextInterface $context'],
				body='if (version_compare($context->getVersion(), "' + from_version + '", "<")) {\n\n    ' + methodBody.replace('\n','\n    ') + '\n}\n'))
		else:
			install_data.add_method(Phpmethod('{}'.format(setupType.lower()),
				params=['SchemaSetupInterface $setup'.format(setupType),'ModuleContextInterface $context'],
				body=methodBody))

		self.add_class(install_data)	


		extension_attributes_xml = Xmlnode('config',attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:framework:Api/etc/extension_attributes.xsd"},nodes=[
			Xmlnode('extension_attributes',attributes={'for':"Magento\Company\Api\Data\CompanyInterface"},match_attributes={'for'},nodes=[
				Xmlnode('attribute',attributes={
					'code':attribute_code,
					'type':'string'
				}, match_attributes=['code'])
			])
		])

		self.add_xml('etc/extension_attributes.xml', extension_attributes_xml)

		company_form_xml = Xmlnode('form',attributes={'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation': "urn:magento:module:Magento_Ui:etc/ui_configuration.xsd"},nodes=[
			Xmlnode('fieldset', attributes={'name': 'general'}, nodes=[
				Xmlnode('field', attributes={'name': attribute_code, 'formElement':frontend_input},nodes=[
					Xmlnode('argument', attributes={'name': 'data', 'xsi:type': 'array'},nodes=[
						Xmlnode('item', attributes={ 'name': 'config', 'xsi:type': 'array'},nodes=[
							Xmlnode('item',
								attributes={
									'name': 'source',
									'xsi:type': 'string',
								},
								node_text=attribute_code
							)
						])
					]),
					Xmlnode('settings', nodes=[
						Xmlnode('label', attributes={'translate': 'true'}, node_text=attribute_label),
						Xmlnode('dataType', node_text='text'),
						Xmlnode('validation', nodes=[
							Xmlnode('rule', attributes={'name': 'required-entry', 'xsi:type': 'boolean'},
									node_text='true' if required else 'false'),
						]),
					])
				])
			])
		])

		self.add_xml('view/base/ui_component/company_form.xml', company_form_xml)
		transformed_attribute_code = "".join([x[0].upper() + x[1:] for x in attribute_code.split("_")])

		self.add_plugin('Magento\\Company\\Model\\Company\\DataProvider', 'getGeneralData', "$result['{attribute_code}'] = $company->getData('{attribute_code}');".format(attribute_code=attribute_code), extra_params=['\\Magento\\Company\\Api\\Data\\CompanyInterface $company'])
		self.add_plugin('Magento\\Company\\Controller\\Adminhtml\\Index\Save', 'setCompanyRequestData', "$result->setData('{attribute_code}', $subject->getRequest()->getPostValue('general')['{attribute_code}']);".format(attribute_code=attribute_code))
		self.add_plugin('Magento\\Company\\Api\\CompanyRepositoryInterface', 'get',
						"$companyExtension->set{transformed_attribute_code}($company->getData('{attribute_code}'));".format(attribute_code=attribute_code, transformed_attribute_code=transformed_attribute_code),
						body_return="$company->setExtensionAttributes($companyExtension);\n\t\treturn $company;",
						body_start="""
		$company = $result;
		$extensionAttributes = $company->getExtensionAttributes();
		$companyExtension = $extensionAttributes ? $extensionAttributes : $this->companyExtensionFactory->create();
		
		""",
						construct=True
		)
		self.add_plugin('Magento\\Company\\Api\\CompanyRepositoryInterface', 'save',
						"$company->setData('{attribute_code}', $extensionAttributes->get{transformed_attribute_code}());".format(
							attribute_code=attribute_code, transformed_attribute_code=transformed_attribute_code),
						body_return="$company->save();\n\t\treturn $company;",
						body_start="""
		$company = $result;
		$extensionAttributes = $company->getExtensionAttributes();
		if (!$extensionAttributes) {
			return $company;
		}
		
		"""
		)
		self.add_plugin('Magento\\Company\\Api\\CompanyRepositoryInterface', 'getList',
						"",
						body_return="return $result;",
						body_start="""
		foreach ($result->getItems() as $company) {
			$this->afterGet($subject, $company);
		}
		"""
		)


		etc_module = Xmlnode('config', attributes={
			'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Module/etc/module.xsd"}, nodes=[
			Xmlnode('module', attributes={'name': self.module_name}, nodes=[
				Xmlnode('sequence', attributes={}, nodes=[
					Xmlnode('module', attributes={'name': 'Magento_Company'})
				])
			])
		])
		self.add_xml('etc/module.xml', etc_module)

	def add_plugin(self, classname, methodname, body, extra_params=[], body_return='return $result;', body_start=False, construct=False):
		plugin = Phpclass('Plugin\\{}'.format(classname))
		if construct:
			plugin = Phpclass('Plugin\\{}'.format(classname),attributes=[
				"""
	/**
	 * @var \Magento\Company\Model\CompanyRepository
	 */
	protected $companyRepository;""",
				"""
    /**
     * @var \Magento\Company\Api\Data\CompanyExtensionFactory
     */
    protected $companyExtensionFactory;"""
			])
			plugin.add_method(
				Phpmethod(
					'__construct',
					params=[
						'\\Magento\\Company\\Model\\CompanyRepository $companyRepository',
						'\\Magento\\Company\\Api\\Data\\CompanyExtensionFactory $companyExtensionFactory'
					],
					body="""
								$this->companyRepository = $companyRepository;
								$this->companyExtensionFactory = $companyExtensionFactory;
								""",
					docstring=[
						'@param \\Magento\\Company\\Model\\CompanyRepository $companyRepository',
						'@param \\Magento\\Company\\Api\\Data\\CompanyExtensionFactory $companyExtensionFactory'
					]
				)
			)

		plugin.add_method(Phpmethod(
			'after' + methodname[0].capitalize() + methodname[1:],
			body=body,
			body_return=body_return,
			body_start=body_start,
			params=[
				'\\' + classname + ' $subject',
				'$result'
			] + extra_params,
			docstring=[
				'@param \\' + classname + ' $subject',
				'@param $result',
				'@return mixed'
			]
		))


		# Add plug first will add the module namespace to PhpClass
		self.add_class(plugin)

		# Plugin XML
		config = Xmlnode('config', attributes={'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation': "urn:magento:framework:ObjectManager/etc/config.xsd"},
		 nodes=[
			 Xmlnode('type', attributes={'name': classname}, nodes=[
				 Xmlnode('plugin', attributes={
					 'name': plugin.class_namespace.replace('\\', '_'),
					 'type': plugin.class_namespace,
					 'sortOrder': '10',
					 'disabled': 'false'
				 })
			 ])
		 ])

		self.add_xml('etc/di.xml', config)


	@classmethod
	def params(cls):
		return [
             SnippetParam(
                name='attribute_label', 
                required=True, 
                description='Example: is_active',
                regex_validator= r'^[a-zA-Z\d\-_\s]+$',
                error_message='Only alphanumeric'),
             SnippetParam(
                 name='required', 
                 default=True,
                 yes_no=True),
             SnippetParam(
                 name='frontend_input', 
                 choises=cls.FRONTEND_INPUT_TYPE,
                 required=True,  
                 default='input'),
			SnippetParam(
				name='upgrade_data',
				default=False,
				yes_no=True
			),
			SnippetParam(
				name='from_version',
				description='1.0.1',
				default='1.0.1'
			),
         ]

	@classmethod
	def extra_params(cls):
		return [
			SnippetParam(
				name='attribute_code',
				description='Default to lowercase of label',
				regex_validator= r'^[a-zA-Z]{1}\w{0,29}$',
				error_message='Only alphanumeric and underscore characters are allowed, and need to start with a alphabetic character. And can\'t be longer then 30 characters'),
		]
