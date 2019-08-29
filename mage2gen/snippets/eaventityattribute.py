# A Magento 2 module generator library
# Copyright (C) 2016 Derrick Heesbeen
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
import os, locale
from .. import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam
from ..utils import upperfirst

class EavEntityAttributeSnippet(Snippet):
	snippet_label = 'EAV Attribute (custom)'

	FRONTEND_INPUT_TYPE = [
		("text","Text Field"),
		("textarea","Text Area"),
		("date","Date"),
		("boolean","Yes/No"),
		("multiselect","Multiple Select"),
		("select","Dropdown"),
		("price","Price"),
		("static","Static")
	]

	STATIC_FIELD_TYPES = [
		("varchar","Varchar"),
		("text","Text"),
		("int","Int"),
		("decimal","Decimal")
	]

	FRONTEND_INPUT_VALUE_TYPE = {
		"text":"varchar",
		"textarea":"text",
		"date":"date",
		"boolean":"int",
		"multiselect":"varchar",
		"select":"int",
		"price":"decimal",
		#"media_image":"",
		#"weee":"",
		#"swatch_visual":"",
		#"swatch_text":""
	}

	description = """
		Install Magento 2 custom eav entity attributes programmatically.
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.count = 1

	def add(self, entity_model_class, attribute_label, frontend_input='text', required=False, options=None, source_model=False, extend_adminhtml_form=False, extra_params=None):
		entity_type = "\{}::ENTITY".format(entity_model_class)
		entity_table = '{}_{}_entity'.format(self._module.package.lower(), entity_model_class.split('\\')[-1].lower())
		extra_params = extra_params if extra_params else {}

		self.count += 1
		value_type = self.FRONTEND_INPUT_VALUE_TYPE.get(frontend_input,'int')
		value_type = value_type if value_type != 'date' else 'datetime'
		user_defined = 'true'
		options = options.split(',') if options else []
		options_php_array = '"'+'","'.join(x.strip() for x in options) + '"'
		options_php_array_string = "array('values' => array("+options_php_array+"))"

		attribute_code = extra_params.get('attribute_code', None)
		if not attribute_code:
			attribute_code = attribute_label.lower().replace(' ','_')[:30]

		split_attribute_code = attribute_code.split('_')
		attribute_code_capitalized = ''.join(upperfirst(item) for item in split_attribute_code)

		if source_model and frontend_input in ['multiselect', 'select']:
			source_model = "\{}\{}\Model\Attribute\Source\{}::class".format(self._module.package, self._module.name, attribute_code_capitalized)
			options_array = []
			for val in options:
				options_array.append("['value' => '" + val.lower() + "', 'label' => __('" + val + "')]")
			options_php_array = '[\n' + ',\n'.join(x.strip() for x in options_array) + '\n]'
			self.add_source_model(attribute_code_capitalized, options_php_array)
			options_php_array_string = "''"
		else:
			source_model = "''"

		templatePath = os.path.join(os.path.dirname(__file__), '../templates/attributes/eavattribute.tmpl')

		with open(templatePath, 'rb') as tmpl:
			template = tmpl.read().decode('utf-8')

		options_php_array_string = options_php_array_string

		methodBody = template.format(
			entity_type=entity_type,
			attribute_code=attribute_code,
			attribute_label=attribute_label,
			value_type=value_type,
			frontend_input=frontend_input,
			user_defined=user_defined,
			required = str(required).lower(),
			options = options_php_array_string,
			unique = 'true' if extra_params.get('unique', False) else 'false',
			default = 'null',
			backend = 'Magento\Eav\Model\Entity\Attribute\Backend\ArrayBackend' if frontend_input == 'multiselect' else '',
			source_model = source_model,
			sort_order = '30',
			frontend = ''
		)

		patchType = 'add'

		install_patch = Phpclass('Setup\\Patch\\Data\\{}{}{}Attribute'.format(patchType, attribute_code_capitalized, entity_model_class.split('\\')[-1]),
			implements=['DataPatchInterface', 'PatchRevertableInterface'],
			dependencies=[
				'Magento\\Framework\\Setup\\Patch\\DataPatchInterface',
				'Magento\\Framework\\Setup\\Patch\\PatchRevertableInterface',
				'Magento\\Framework\\Setup\\ModuleDataSetupInterface',
				'Magento\\Eav\\Setup\\EavSetupFactory',
				'Magento\\Eav\\Setup\\EavSetup',
			],
			attributes=[
				"/**\n\t * @var ModuleDataSetupInterface\n\t */\n\tprivate $moduleDataSetup;",
				"/**\n\t * @var EavSetupFactory\n\t */\n\tprivate $eavSetupFactory;"
			]
		)

		install_patch.add_method(Phpmethod(
			'__construct',
			params=[
				'ModuleDataSetupInterface $moduleDataSetup',
				'EavSetupFactory $eavSetupFactory'
			],
			body="$this->moduleDataSetup = $moduleDataSetup;\n$this->eavSetupFactory = $eavSetupFactory;",
			docstring=[
				'Constructor',
				'',
				'@param ModuleDataSetupInterface $moduleDataSetup',
				'@param EavSetupFactory $eavSetupFactory'
			]
		))

		install_patch.add_method(Phpmethod(
			'apply',
			body_start='$this->moduleDataSetup->getConnection()->startSetup();',
			body_return='$this->moduleDataSetup->getConnection()->endSetup();',
			body="""
		/** @var EavSetup $eavSetup */
$eavSetup = $this->eavSetupFactory->create(['setup' => $this->moduleDataSetup]);
""" + methodBody,
			docstring=[
				'{@inheritdoc}',
			]
		))

		install_patch.add_method(Phpmethod(
			'revert',
			body_start='$this->moduleDataSetup->getConnection()->startSetup();',
			body_return='$this->moduleDataSetup->getConnection()->endSetup();',
			body="""
				/** @var EavSetup $eavSetup */
		$eavSetup = $this->eavSetupFactory->create(['setup' => $this->moduleDataSetup]);
		$eavSetup->removeAttribute({entity_type}, '{attribute_code}');""".format(entity_type=entity_type, attribute_code=attribute_code)
		))
		install_patch.add_method(Phpmethod(
			'getAliases',
			body="return [];",
			docstring=[
				'{@inheritdoc}'
			]
		))

		install_patch.add_method(Phpmethod(
			'getDependencies',
			access='public static',
			body="return [\n\n];",
			docstring=[
				'{@inheritdoc}'
			]
		))

		self.add_class(install_patch)


		etc_module = Xmlnode('config', attributes={
			'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Module/etc/module.xsd"}, nodes=[
			Xmlnode('module', attributes={'name': self.module_name}, nodes=[
				Xmlnode('sequence', attributes={}, nodes=[
					Xmlnode('module', attributes={'name': 'Magento_Eav'})
				])
			])
		])
		self.add_xml('etc/module.xml', etc_module)

		if extend_adminhtml_form:
			# UI Component Form
			ui_form = Xmlnode('form', nodes=[
				Xmlnode('fieldset', attributes={'name': 'general'}, nodes=[
					Xmlnode('field', attributes={'name': attribute_code, 'formElement': frontend_input,
												 'sortOrder': str(10 * self.count)}, nodes=[
						Xmlnode('argument', attributes={'name': 'data', 'xsi:type': 'array'}, nodes=[
							Xmlnode('item', attributes={'name': 'config', 'xsi:type': 'array'}, nodes=[
								Xmlnode('item', attributes={'name': 'source', 'xsi:type': 'string'},
										node_text=attribute_code),
							]),
						]),
						Xmlnode('settings', nodes=[
							Xmlnode('dataType', node_text='text'),
							Xmlnode('label', attributes={'translate': 'true'}, node_text=attribute_label),
							Xmlnode('dataScope', node_text=attribute_code),
							Xmlnode('validation', nodes=[
								Xmlnode('rule', attributes={'name': 'required-entry', 'xsi:type': 'boolean'},
										node_text='true' if required else 'false'),
							]),
						]),
					]),
				]),
			])
			self.add_xml('view/adminhtml/ui_component/{}_form.xml'.format(entity_table), ui_form)

	def add_source_model(self, attribute_code_capitalized, options_php_array_string):
		source_model = Phpclass('Model\\Attribute\Source\\{}'.format(upperfirst(attribute_code_capitalized)),
			extends='\\Magento\\Eav\\Model\\Entity\\Attribute\\Source\\AbstractSource')

		source_model.add_method(Phpmethod(
			'getAllOptions',
			body="$this->_options = " + options_php_array_string + ";\n"
				 "return $this->_options;",
			docstring=[
				'getAllOptions',
				'',
				'@return array'
			]
		))
		self.add_class(source_model)

	@classmethod
	def params(cls):
		 return [
			 SnippetParam(
				 name='entity_model_class',
				 required=True,
				 description='Example: Magento\Customer\Model\Customer',
				regex_validator=r'^[\w\\]+$',
				error_message='Only alphanumeric, underscore and backslash characters are allowed'),
			 SnippetParam(
				name='attribute_label',
				required=True,
				description='Example: color',
				regex_validator= r'^[a-zA-Z\d\-_\s]+$',
				error_message='Only alphanumeric'),
			 SnippetParam(
				 name='frontend_input',
				 choises=cls.FRONTEND_INPUT_TYPE,
				 required=True,
				 default='text'),
			 SnippetParam(
				 name='options',
				 depend={'frontend_input': r'select|multiselect'},
				 required=False,
				 description='Dropdown or Multiselect options comma seperated',
				 error_message='Only alphanumeric'),
			 SnippetParam(
				 name='source_model',
				 depend={'frontend_input': r'select|multiselect'},
				 required=False,
				 default=False,
				 yes_no=True),
			 SnippetParam(
				 name='required',
				 required=True,
				 default=True,
				 yes_no=True),
			 SnippetParam(name='extend_adminhtml_form', yes_no=True, description='Extend the admin ui based on the Entity Model Class'),

		 ]

	@classmethod
	def extra_params(cls):
		 return [
			SnippetParam(
				name='attribute_code',
				description='Default to lowercase of label',
				regex_validator= r'^[a-zA-Z]{1}\w{0,29}$',
				error_message='Only alphanumeric and underscore characters are allowed, and need to start with a alphabetic character. And can\'t be longer then 30 characters'),
			 SnippetParam(
				 name='unique',
				 required=True,
				 default=False,
				 yes_no=True),
		]
