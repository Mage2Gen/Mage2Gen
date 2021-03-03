# Copyright © Experius All rights reserved.
# See COPYING.txt for license details.

import os, locale
from .. import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam, Readme
from ..utils import upperfirst


class CategoryAttributeSnippet(Snippet):
    snippet_label = 'Category Attribute'

    FRONTEND_INPUT_TYPE = [
        ("text", "Text Field"),
        ("textarea", "Text Area"),
        ("date", "Date"),
        ("boolean", "Yes/No"),
        ("multiselect", "Multiple Select"),
        ("select", "Dropdown"),
        ("price", "Price"),
        ("static", "Static"),
        ("image", "Image")
    ]

    STATIC_FIELD_TYPES = [
        ("varchar", "Varchar"),
        ("text", "Text"),
        ("int", "Int"),
        ("decimal", "Decimal")
    ]

    FRONTEND_INPUT_VALUE_TYPE = {
        "text": "varchar",
        "textarea": "text",
        "date": "date",
        "boolean": "int",
        "multiselect": "varchar",
        "select": "int",
        "price": "decimal",
        "image": "varchar"
    }

    FRONTEND_FORM_ELEMENT = {
        "text": "input",
        "textarea": "textarea",
        "checkbox": "checkbox",
        "select": "select",
        "multiselect": "multiselect",
        "date": "date",
        "image": "fileUploader"
    }

    SCOPE_CHOICES = [
        ("ScopedAttributeInterface::SCOPE_STORE", "SCOPE_STORE"),
        ("ScopedAttributeInterface::SCOPE_GLOBAL", "SCOPE_GLOBAL"),
        ("ScopedAttributeInterface::SCOPE_WEBSITE", "SCOPE_WEBSITE")
    ]

    CATEGORY_SOURCE_MODELS = [
        ('Magento\Eav\Model\Entity\Attribute\Source\Boolean', 'Magento\Eav\Model\Entity\Attribute\Source\Boolean'),
        (
        'Magento\Catalog\Model\Category\Attribute\Source\Page', 'Magento\Catalog\Model\Category\Attribute\Source\Page'),
        (
        'Magento\Catalog\Model\Category\Attribute\Source\Mode', 'Magento\Catalog\Model\Category\Attribute\Source\Mode'),
        ('Magento\Catalog\Model\Category\Attribute\Source\Sortby',
         'Magento\Catalog\Model\Category\Attribute\Source\Sortby'),
        ('', '------------------'),
        ('custom', 'Create Your own')
    ]

    CATEGORY_BACKEND_MODELS = [
        ('Magento\Catalog\Model\Category\Attribute\Backend\Image',
         'Magento\Catalog\Model\Category\Attribute\Backend\Image')
    ]

    description = """
		Install Magento 2 category attributes programmatically. 
	"""

    def add(self, attribute_label, frontend_input='text', scope="ScopedAttributeInterface::SCOPE_STORE", required=False,
            upgrade_data=False, from_version='1.0.1', source_model=False, source_model_options=False,
            extra_params=None):
        extra_params = extra_params if extra_params else {}

        value_type = self.FRONTEND_INPUT_VALUE_TYPE.get(frontend_input, 'int')
        value_type = value_type if value_type != 'date' else 'datetime'

        form_element = self.FRONTEND_FORM_ELEMENT.get(frontend_input, 'input')

        user_defined = 'false'
        backend_model = ''

        attribute_code = extra_params.get('attribute_code', None)
        if not attribute_code:
            attribute_code = attribute_label.lower().replace(' ', '_')[:30]
        if frontend_input == 'select' and not source_model:
            source_model = "Magento\Eav\Model\Entity\Attribute\Source\Boolean"
        elif frontend_input == 'multiselect':
            backend_model = "Magento\Eav\Model\Entity\Attribute\Backend\ArrayBackend"
            if not source_model:
                source_model = "Magento\Catalog\Model\Category\Attribute\Source\Page"
        elif frontend_input == "image":
            source_model = ''
            backend_model = "Magento\Catalog\Model\Category\Attribute\Backend\Image"
        elif frontend_input != 'multiselect' and frontend_input != 'select':
            source_model = ''
            backend_model = ''

        split_attribute_code = attribute_code.split('_')
        attribute_code_capitalized = ''.join(upperfirst(item) for item in split_attribute_code)

        # customer source model
        if source_model == 'custom' and source_model_options and frontend_input == 'select' or frontend_input == 'multiselect':
            source_model_class = Phpclass(
                'Model\\Category\\Attribute\\Source\\' + ''.join(n.capitalize() for n in attribute_code.split('_')),
                extends='\Magento\Eav\Model\Entity\Attribute\Source\AbstractSource',
                attributes=[
                    'protected $_optionsData;'
                ]
            )

            source_model_class.add_method(Phpmethod('__construct',
                                                    params=['array $options'],
                                                    body="$this->_optionsData = $options;",
                                                    docstring=[
                                                        'Constructor',
                                                        '',
                                                        '@param array $options',
                                                    ]
                                                    ))

            if frontend_input == 'select':
                to_option_array = "[\n        {}\n    ]".format(',\n        '.join(
                    "['value' => '{1}', 'label' => __('{0}')]".format(value.strip(), index + 1) for index, value in
                    enumerate(source_model_options.split(',')))
                )
            else:
                to_option_array = "[\n        {}\n    ]".format(',\n        '.join(
                    "['value' => (string) '{0}', 'label' => __('{0}')]".format(value.strip()) for value in
                    source_model_options.split(','))
                )

            source_model_class.add_method(Phpmethod('getAllOptions',
                                                    body="""
				if ($this->_options === null) {{
				    $this->_options = {options};
				}}
				return $this->_options;
				""".format(options=to_option_array),
                                                    docstring=[
                                                        'getAllOptions',
                                                        '',
                                                        '@return array',
                                                    ]
                                                    ))
            self.add_class(source_model_class)

            source_model = source_model_class.class_namespace

        sort_order = extra_params.get('sort_order', '333') if extra_params.get('sort_order', '333') else '333'

        templatePath = os.path.join(os.path.dirname(__file__), '../templates/attributes/categoryattribute.tmpl')

        with open(templatePath, 'rb') as tmpl:
            template = tmpl.read().decode('utf-8')

        methodBody = template.format(
            attribute_code=attribute_code,
            attribute_label=attribute_label,
            value_type=value_type,
            frontend_input=frontend_input,
            user_defined=user_defined,
            scope=scope,
            required=str(required).lower(),
            default='null',
            sort_order=sort_order,
            source_model=source_model,
            backend_model=backend_model
        )

        patchType = 'add'
        # TODO: add Upgrade Attribute Support

        if upgrade_data:
            patchType = 'add'

        install_patch = Phpclass(
            'Setup\\Patch\\Data\\{}{}CategoryAttribute'.format(patchType, attribute_code_capitalized),
            implements=['DataPatchInterface', 'PatchRevertableInterface'],
            dependencies=[
                'Magento\\Framework\\Setup\\Patch\\DataPatchInterface',
                'Magento\\Framework\\Setup\\Patch\\PatchRevertableInterface',
                'Magento\\Framework\\Setup\\ModuleDataSetupInterface',
                'Magento\\Eav\\Setup\\EavSetupFactory',
                'Magento\\Eav\\Setup\\EavSetup',
                'Magento\\Eav\\Model\\Entity\\Attribute\\ScopedAttributeInterface'
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
		$eavSetup->removeAttribute(\Magento\Catalog\Model\Category::ENTITY, '{attribute_code}');""".format(
                attribute_code=attribute_code)
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

        category_form_file = 'view/adminhtml/ui_component/category_form.xml'

        if frontend_input == 'select' or frontend_input == 'multiselect':
            options_xml = Xmlnode('item', attributes={'name': 'options', 'xsi:type': 'object'}, node_text=source_model)
        else:
            options_xml = False

        if frontend_input == 'image':
            image_xml = [
                Xmlnode('item', attributes={'name': 'uploaderConfig', 'xsi:type': 'array'}, nodes=[Xmlnode('item',
                                                                                                           attributes={
                                                                                                               'name': 'url',
                                                                                                               'xsi:type': 'url',
                                                                                                               'path': 'catalog/category_image/upload'})]),
                Xmlnode('item', attributes={'name': 'elementTmpl', 'xsi:type': 'string'},
                        node_text='ui/form/element/uploader/uploader'),
                Xmlnode('item', attributes={'name': 'previewTmpl', 'xsi:type': 'string'},
                        node_text='Magento_Catalog/image-preview')
            ]

        else:
            image_xml = []

        required_value = 'true' if required else 'false'
        required_xml = Xmlnode('item', attributes={'name': 'required', 'xsi:type': 'boolean'}, node_text=required_value)
        required_entry_xml = Xmlnode('item', attributes={'name': 'validation', 'xsi:type': 'array'}, nodes=[
            Xmlnode('item', attributes={'name': 'required-entry', 'xsi:type': 'boolean'}, node_text=required_value)])

        item_xml = [
            required_xml,
            required_entry_xml,
            Xmlnode('item', attributes={'name': 'sortOrder', 'xsi:type': 'number', }, node_text=sort_order),
            Xmlnode('item', attributes={'name': 'dataType', 'xsi:type': 'string'}, node_text='string'),
            Xmlnode('item', attributes={'name': 'formElement', 'xsi:type': 'string'}, node_text=form_element),
            Xmlnode('item', attributes={'name': 'label', 'xsi:type': 'string', 'translate': 'true'},
                    node_text=attribute_label)
        ]

        item_xml.extend(image_xml)

        category_form_xml = Xmlnode('form', attributes={'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                                                        'xsi:noNamespaceSchemaLocation': "urn:magento:module:Magento_Ui:etc/ui_configuration.xsd"},
                                    nodes=[
                                        Xmlnode('fieldset', attributes={'name': 'general'}, nodes=[
                                            # Xmlnode('argument',attributes={'name':'data','xsi:type':'array'},nodes=[
                                            #     Xmlnode('item',attributes={'name':'config','xsi:type':'array'},nodes=[
                                            #         Xmlnode('item',attributes={'name':'label','xsi:type':'string','translate':'true'},node_text='test'),
                                            #         Xmlnode('item',attributes={'name':'collapsible','xsi:type':'boolean'},node_text='true'),
                                            #         Xmlnode('item',attributes={'name':'sortOrder','xsi:type':'number'},node_text='100'),
                                            #     ])
                                            # ]),
                                            Xmlnode('field', attributes={'name': attribute_code}, nodes=[
                                                Xmlnode('argument', attributes={'name': 'data', 'xsi:type': 'array'},
                                                        nodes=[
                                                            options_xml,
                                                            Xmlnode('item',
                                                                    attributes={'name': 'config', 'xsi:type': 'array'},
                                                                    nodes=item_xml)
                                                        ])
                                            ])
                                        ])
                                    ])

        etc_module = Xmlnode('config', attributes={
            'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Module/etc/module.xsd"}, nodes=[
            Xmlnode('module', attributes={'name': self.module_name}, nodes=[
                Xmlnode('sequence', attributes={}, nodes=[
                    Xmlnode('module', attributes={'name': 'Magento_Catalog'})
                ])
            ])
        ])
        self.add_xml('etc/module.xml', etc_module)

        self.add_xml(category_form_file, category_form_xml)

        self.add_static_file(
            '.',
            Readme(
                attributes=" - Category - {} ({})".format(attribute_label, attribute_code),
            )
        )

    @classmethod
    def params(cls):
        return [
            SnippetParam(
                name='attribute_label',
                required=True,
                description='Example: short_description',
                regex_validator=r'^[a-zA-Z\d\-_\s]+$',
                error_message='Only alphanumeric'),
            SnippetParam(
                name='frontend_input',
                choises=cls.FRONTEND_INPUT_TYPE,
                required=True,
                default='text'),
            SnippetParam(
                name='source_model',
                choises=cls.CATEGORY_SOURCE_MODELS,
                depend={'frontend_input': r'select|multiselect'},
                default='Magento\Eav\Model\Entity\Attribute\Source\Boolean'),
            SnippetParam(
                name='source_model_options',
                required=True,
                depend={'source_model': r'custom'},
                description='Dropdown or Multiselect options comma seperated',
                error_message='Only alphanumeric'),
            SnippetParam(
                name='scope',
                required=True,
                choises=cls.SCOPE_CHOICES,
                default='ScopedAttributeInterface::SCOPE_STORE'),
            SnippetParam(
                name='required',
                required=True,
                default=False,
                yes_no=True),
            # TODO: add Upgrade Attribute Support
            # SnippetParam(
            #  name='upgrade_data',
            #  default=False,
            #  yes_no=True
            # )
        ]

    @classmethod
    def extra_params(cls):
        return [
            SnippetParam(
                name='attribute_code',
                description='Default to lowercase of label',
                regex_validator=r'^[a-zA-Z]{1}\w{0,29}$',
                error_message='Only alphanumeric and underscore characters are allowed, and need to start with a alphabetic character. And can\'t be longer then 30 characters'
            ),
            SnippetParam(
                name='sort_order',
                description='333',
                regex_validator=r'^\d+$',
                error_message='Only numeric value'
            )
        ]
