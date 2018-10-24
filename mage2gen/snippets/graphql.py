# A Magento 2 module generator library
# Copyright (C) 2018 Derrick Heesbeen
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
from .. import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam
from ..utils import upperfirst


class GraphQlSnippet(Snippet):
    snippet_label = 'GraphQl'

    description = """
	
	"""

    def add(self, repository_interface_classname, data_interface_classname, extra_params=None):
        original_vendor_name = repository_interface_classname.split('\\')[0]
        original_module_name = repository_interface_classname.split('\\')[1]
        splitted_data_interface_classname = data_interface_classname.split('\\')[-1];
        splitted_repository_interface_classname = repository_interface_classname.split('\\')[-1];
        model_name = splitted_data_interface_classname.replace('Interface', '').lower()
        model_id = '{}_id'.format(model_name).upper()

        data_provider = Phpclass(
            'Model\\Resolver\\DataProvider\\{}'.format(upperfirst(model_name)),
            dependencies=[
                repository_interface_classname,
                data_interface_classname,
                'Magento\\Framework\\Exception\\NoSuchEntityException',
                'Magento\\Widget\\Model\\Template\\FilterEmulate'
            ],
            attributes=[
                'private ${}Repository;'.format(model_name),
                'private $widgetFilter;'
            ]
        )

        data_provider.add_method(
            Phpmethod(
                '__construct',
                params=[
                    '{} ${}Repository'.format(splitted_repository_interface_classname, model_name),
                    'FilterEmulate $widgetFilter'
                ],
                body="""
						$this->{0}Repository = ${0}Repository;
						$this->widgetFilter = $widgetFilter;""".format(model_name),
                docstring=[
                    '@param \\{} ${}Repository'.format(repository_interface_classname, model_name),
                    '@param \\Magento\\Widget\\Model\\Template\\FilterEmulate $widgetFilter'
                ]
            )
        )

        data_provider.add_method(
            Phpmethod(
                'getData',
                params=[
                    'string ${}Identifier'.format(model_name)
                ],
                body="""
						${0} = $this->{0}Repository->getById(${0}Identifier);

						$blockData = [
						    {1}::{2} => ${0}->getIdentifier()
						];
						return ${0}Data;""".format(model_name, splitted_data_interface_classname, model_id),
                docstring=[
                    '@param string ${}Repository'.format(model_name),
                    '@return array',
                    '@return NoSuchEntityException'
                ]
            )
        )

        self.add_class(data_provider)

        resolver = Phpclass(
            'Model\\Resolver\\{}s'.format(upperfirst(model_name)),
            implements=['ResolverInterface'],
            dependencies=[
                'Magento\\Framework\\Exception\\NoSuchEntityException',
                'Magento\\Framework\\GraphQl\\Config\\Element\\Field',
                'Magento\\Framework\\GraphQl\\Exception\\GraphQlInputException',
                'Magento\\Framework\\GraphQl\\Exception\\GraphQlNoSuchEntityException',
                'Magento\\Framework\\GraphQl\\Query\\ResolverInterface',
                'Magento\\Framework\\GraphQl\\Schema\\Type\\ResolveInfo',
            ],
            attributes=[
                'private ${}DataProvider;'.format(model_name)
            ]
        )

        resolver.add_method(
            Phpmethod(
                '__construct',
                params=[
                    'DataProvider\\{} ${}DataProvider'.format(upperfirst(model_name),model_name)
                ],
                body="$this->{0}DataProvider = ${0}DataProvider;".format(model_name),
                docstring=[
                    '@param DataProvider\\{} ${}Repository'.format(upperfirst(model_name), model_name)
                ]
            )
        )

        resolver.add_method(
            Phpmethod(
                'resolve',
                params=[
                    'Field $field',
                    '$context',
                    'ResolveInfo $info',
                    'array $value = null',
                    'array $args = null'
                ],
                body="""
						${0}Identifiers = $this->get{1}Identifiers($args);
						${0}sData = $this->get{1}sData(${0}Identifiers);
        
						$resultData = [
						    'items' => ${0}sData,
						];
						return $resultData;""".format(model_name, upperfirst(model_name)),
                docstring=[
                    '@inheritdoc'
                ]
            )
        )

        resolver.add_method(
            Phpmethod(
                'get{}Identifiers'.format(upperfirst(model_name)),
                params=[
                    'array $args'
                ],
                body="""
						if (!isset($args['identifiers']) || !is_array($args['identifiers']) || count($args['identifiers']) === 0) {{
						    throw new GraphQlInputException(__('"identifiers" of {original_vendor_name} {original_module_name}s should be specified'));
						}}

						return $args['identifiers'];""".format(
                            original_vendor_name=original_vendor_name,
                            original_module_name=original_module_name
                        ),
                docstring=[
                    '@inheritdoc'
                ],
                access='private'
            )
        )

        resolver.add_method(
            Phpmethod(
                'get{}sData'.format(upperfirst(model_name)),
                params=[
                    'array ${}Identifiers'.format(model_name)
                ],
                body="""
						${model_name}sData = [];
						try {{
						    foreach (${model_name}Identifiers as ${model_name}Identifier) {{
						        ${model_name}sData[${model_name}Identifier] = $this->{model_name}DataProvider->getData(${model_name}Identifier);
						    }}
						}} catch (NoSuchEntityException $e) {{
						    throw new GraphQlNoSuchEntityException(__($e->getMessage()), $e);
						}}
						return ${model_name}sData;""".format(
                    model_name=model_name
                ),
                docstring=[
                    '@param array ${}Identifiers'.format(model_name),
                    '@return array',
                    '@throws GraphQlNoSuchEntityException'
                ],
                access='private'
            )
        )

        self.add_class(resolver)

        path = 'etc'
        self.add_static_file(path, StaticFile(
                'schema.graphqls',
                body="""type Query {{
    {original_vendor_name_lower}{original_module_name}s (
        identifiers: [String] @doc(description: "Identifiers of the {original_vendor_name} {original_module_name}s")
    ): {original_vendor_name}{original_module_name}s @resolver(class: "{vendor}\\\\{module_name}\\\\Model\\\\Resolver\\\\{model_name}s") @doc(description: "The {original_vendor_name} {original_module_name} query returns information about {original_vendor_name} {original_module_name}s")
}}
type {original_vendor_name}{original_module_name}s @doc(description: "{original_module_name} {original_module_name}s information") {{
    items: [{original_vendor_name}{original_module_name}] @doc(description: "An array of {original_module_name} {original_module_name}")
}}

type {original_vendor_name}{original_module_name} @doc(description: "{original_vendor_name} {original_module_name} defines all {original_vendor_name} {original_module_name} information") {{
    {model_id}: String @doc(description: "{original_vendor_name} {original_module_name} {model_id}")
}}""".format(
                    original_vendor_name=original_vendor_name,
                    original_vendor_name_lower=original_vendor_name.lower(),
                    original_module_name=original_module_name,
                    model_name=upperfirst(model_name),
                    vendor=self._module.package,
                    module_name=self._module.name,
                    model_id=model_id.lower()
                )
            )
         )
        sequenceModules = [
            Xmlnode('module', attributes={'name': 'Magento_GraphQl'})
        ]
        if '{}_{}'.format(original_vendor_name, original_module_name) != '{}_{}'.format(self._module.package, self._module.name):
            sequenceModules.append(Xmlnode('module', attributes={'name': '{}_{}'.format(original_vendor_name, original_module_name)}))
        etc_module = Xmlnode('config', attributes={
            'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Module/etc/module.xsd"}, nodes=[
            Xmlnode('module', attributes={'name': self.module_name}, nodes=[
                Xmlnode('sequence', attributes={}, nodes=sequenceModules)
            ])
        ])
        self.add_xml('etc/module.xml', etc_module)

    @classmethod
    def params(cls):
        return [
            SnippetParam(
                name='repository_interface_classname', required=True,
                description='Example: Magento\Cms\Api\BlockRepositoryInterface',
                regex_validator=r'^[\w\\]+$',
                error_message='Only alphanumeric, underscore and backslash characters are allowed'
            ),
            SnippetParam(
                name='data_interface_classname', required=True,
                description='Example: Magento\Cms\Api\Data\BlockInterface',
                regex_validator=r'^[\w\\]+$',
                error_message='Only alphanumeric, underscore and backslash characters are allowed'
            ),
        ]


