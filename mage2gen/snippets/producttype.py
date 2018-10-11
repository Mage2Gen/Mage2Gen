# A Magento 2 module generator library
# Copyright (C) 2016 Derrick Heesbeen
# Copyright (C) 2016 Maikel Martens Changed add API and refactor code
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


class ProductTypeSnippet(Snippet):
    snippet_label = 'Product Type'

    description = """Creates a Product Type

    	Magento supports a number of product types, each with its own behavior and attributes. 
    	
    	This powerful concept allows Magento to support a wide range of industries and merchant needs by mixing and matching product experiences in their catalog. 

    	Even more powerful, however, is the ability for developers to easily add new product types.
    	
    	In general, when a product class has distinct behavior or attributes, it should be represented by its own product type. 
    	
    	This allows the product type to have complex and custom logic and presentation, 
    	
    	with no impact on other product types — ensuring that native product types can continue to function as intended.

    	"""

    STATIC_PRODUCT_TYPES = [
        ("default", "Default"),
        ("simple", "Simple Product"),
        ("virtual", "Virtual Product"),
        ("configurable", "Configurable Product"),
        ("grouped", "Grouped Product"),
        ("downloadable", "Downloadable Product"),
        ("bundle", "Bundle Product"),
        ("giftcard", "Giftcard Product(Enterprise Edition Only)")
    ]

    STATIC_PRODUCT_TYPES_SOURCE_MODELS = {
        'default': '\\Magento\\Catalog\\Model\\Product\\Type\\AbstractType',
        'simple': '\\Magento\\Catalog\\Model\\Product\\Type\\Simple',
        'virtual': '\\Magento\\Catalog\\Model\\Product\\Type\\Virtual',
        'configurable': '\\Magento\\ConfigurableProduct\\Model\\Product\\Type\\Configurable',
        'grouped': '\\Magento\\GroupedProduct\\Model\\Product\\Type\\Grouped',
        'downloadable': '\\Magento\\Downloadable\\Model\\Product\\Type',
        'bundle': '\\Magento\\Bundle\\Model\\Product\\Type',
        'giftcard': '\\Magento\\GiftCard\\Model\\Catalog\\Product\\Type\\Giftcard'
    }


    def add(self, product_type_code, product_type_label, extend_product_type='default', use_composable_types=False, use_price_model=False, upgrade_data=False, from_version='1.0.1', extra_params=None):

        extend_product_type_class = self.STATIC_PRODUCT_TYPES_SOURCE_MODELS.get(extend_product_type, '\\Magento\\Catalog\\Model\\Product\\Type\\AbstractType')

        product_type_code = product_type_code.lower().replace(' ', '_')

        product_type_class = Phpclass('Model\\Product\\Type\\{}'.format(upperfirst(product_type_code)), extends=extend_product_type_class, attributes=[
            "const TYPE_ID = '{}';".format(product_type_code)
        ])

        product_type_class.add_method(Phpmethod(
            'deleteTypeSpecificData',
            params=[
                '\Magento\Catalog\Model\Product $product',
            ],
            body="// method intentionally empty",
            docstring=['{@inheritdoc}']

        ))
        self.add_class(product_type_class)

        product_type_class_name = product_type_class.class_namespace

        if use_composable_types:
            composable_types_xml = Xmlnode(
                'composableTypes',
                nodes=[
                    Xmlnode('type',
                            attributes={
                                'name': product_type_code.lower()
                            }
                    )
                ]
            )
        else:
            composable_types_xml = False

        if use_price_model:

            price_model_class = Phpclass('Model\\Product\\Price',
                                          extends='\\Magento\\Catalog\\Model\\Product\\Type\\Price', attributes=[])
            self.add_class(price_model_class)
            price_model_class_name = "{}\{}\Model\Product\Price".format(self._module.package, self._module.name)
            price_model_xml = Xmlnode('priceModel', attributes={'instance': price_model_class_name})
        else:
            price_model_xml = False

        product_type_xml = Xmlnode('config', attributes={'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance', 'xsi:noNamespaceSchemaLocation': "urn:magento:module:Magento_Catalog:etc/product_types.xsd"},
            nodes=[
                Xmlnode(
                    'type',
                        attributes={
                            'name': product_type_code.lower(),
                            'label': format(upperfirst(product_type_label)),
                            'modelInstance': product_type_class_name
                        },
                        nodes=[
                            price_model_xml
                        ]
                ),
                composable_types_xml,
            ]);

        self.add_xml('etc/product_types.xml', product_type_xml)

        templatePath = os.path.join(os.path.dirname(__file__), '../templates/producttype.tmpl')

        with open(templatePath, 'rb') as tmpl:
            template = tmpl.read().decode('utf-8')

        methodBody = template.format(
            product_type_class_name="\{}".format(product_type_class_name)
        )

        setupType = 'Install'
        if upgrade_data:
            setupType = 'Upgrade'

        install_data = Phpclass('Setup\\{}Data'.format(setupType),
            implements=['{}DataInterface'.format(setupType)],
            dependencies=[
                'Magento\\Framework\\Setup\\{}DataInterface'.format(setupType),
                'Magento\\Framework\\Setup\\ModuleContextInterface',
                'Magento\\Framework\\Setup\\ModuleDataSetupInterface',
                'Magento\\Eav\\Setup\\EavSetup',
                'Magento\\Eav\\Setup\\EavSetupFactory'],
            attributes=[
                'private $eavSetupFactory;'
            ])

        install_data.add_method(Phpmethod(
            '__construct',
            params=['EavSetupFactory $eavSetupFactory'],
            body="$this->eavSetupFactory = $eavSetupFactory;",
            docstring=[
                'Constructor',
                '',
                '@param \\Magento\\Eav\\Setup\\EavSetupFactory $eavSetupFactory'
            ]
        ))

        install_data.add_method(Phpmethod('{}'.format(setupType.lower()),
            params=['ModuleDataSetupInterface $setup', 'ModuleContextInterface $context'],
            body="$eavSetup = $this->eavSetupFactory->create(['setup' => $setup]);",
            docstring=['{@inheritdoc}']))
        if upgrade_data:
            install_data.add_method(Phpmethod('{}'.format(setupType.lower()),
                params=['ModuleDataSetupInterface $setup', 'ModuleContextInterface $context'],
                body='if (version_compare($context->getVersion(), "' + from_version + '", "<")) {\n\n    ' + methodBody.replace('\n','\n    ') + '\n}\n'))
        else:
            install_data.add_method(Phpmethod('{}'.format(setupType.lower()),
                params=['ModuleDataSetupInterface $setup', 'ModuleContextInterface $context'],
                body=methodBody))

        self.add_class(install_data)


    @classmethod
    def params(cls):
        return [
            SnippetParam(
                name='product_type_code',
                required=True,
                description='Product Type Code',
                regex_validator=r'^[a-zA-Z]{1}[a-zA-Z]+$',
                error_message='Only alphanumeric are allowed, and need to start with a alphabetic character.'
            ),
            SnippetParam(
                name='product_type_label',
                required=True,
                description='Product Type Label',
                regex_validator=r'^[a-zA-Z]{1}[a-zA-Z]+$',
                error_message='Only alphanumeric are allowed, and need to start with a alphabetic character.'
            ),
            SnippetParam(
                name='extend_product_type',
                choises=cls.STATIC_PRODUCT_TYPES,
                required=True,
                default='default'
            ),
            SnippetParam(
                name='use_composable_types',
                default=False,
                yes_no=True
            ),
            SnippetParam(
                name='use_price_model',
                default=False,
                yes_no=True
            ),
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
