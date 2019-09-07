# A Magento 2 module generator library
# Copyright (C) 2018 Lewis Voncken
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
from .. import Module, Phpclass, Phpmethod, Xmlnode, Snippet, SnippetParam, GraphQlSchema, GraphQlObjectType, \
    GraphQlObjectItem, StaticFile
from ..utils import upperfirst, lowerfirst


class GraphQlSnippet(Snippet):
    snippet_label = 'GraphQl'

    description = """

	"""

    GRAPHQL_TYPE_CHOISES = [
        ('Query', 'Query'),
        ('Mutation', 'Mutation'),
        ('Custom', 'Custom')
    ]

    def add(self, base_type, identifier, custom_type=False, description='', object_arguments=False, object_fields=False,
            data_provider_dependency=False, add_cache_identity=False, extra_params=None):

        if not object_fields:
            object_fields = 'id'
            if object_arguments:
                object_fields = object_arguments

        if custom_type:
            identifier = custom_type
        identifier = lowerfirst(identifier)
        item_identifier = upperfirst(identifier)
        resolver_graphqlformat = '{}\\\{}\\\Model\\\Resolver\\\{}'.format(self._module.package, self._module.name,
                                                                          item_identifier)

        cache_identity_graphqlformat = ''
        if add_cache_identity and item_identifier and base_type == 'Query':
            object_id = object_fields.split(',')[0]
            cache_identity_graphqlformat = '{}\\\{}\\\Model\\\Resolver\\\{}\\Identity'.format(self._module.package, self._module.name,
                                                                          item_identifier)
            if add_cache_identity:
                cacheIdentity = Phpclass(
                    'Model\\Resolver\\{}\\Identity'.format(item_identifier),
                    implements=['IdentityInterface'],
                    dependencies=[
                        'Magento\\Framework\\GraphQl\\Query\\Resolver\\IdentityInterface',
                    ],
                    attributes=[
                        'private $cacheTag = \Magento\Framework\App\Config::CACHE_TAG;'
                    ]
                )
                cacheIdentity.add_method(
                    Phpmethod(
                        'getIdentities',
                        params=[
                            'array $resolvedData'
                        ],
                        body="""
            $ids =  empty($resolvedData['{object_id}']) ?
                [] : [$this->cacheTag, sprintf('%s_%s', $this->cacheTag, $resolvedData['{object_id}'])];

            return $ids;""".format(object_id=object_id),
                        docstring=[
                            '@param array $resolvedData',
                            '@return string[]'
                        ]
                    )
                )
                self.add_class(cacheIdentity)

        item_type = 'String'
        if base_type == 'Custom':
            item_type = identifier

        if base_type == 'Query':
            item_type = item_identifier

        schema = GraphQlSchema()

        if base_type != 'Custom':
            base_object_type = GraphQlObjectType(
                base_type
            )

            base_object_type.add_objectitem(
                GraphQlObjectItem(
                    identifier,
                    item_arguments=object_arguments,
                    item_type=item_type,
                    item_resolver=resolver_graphqlformat,
                    item_cache_identity=cache_identity_graphqlformat,
                    description=description
                )
            )

            schema.add_objecttype(
                base_object_type
            )

        item_definition = GraphQlObjectType(
            item_identifier
        )

        for object_field in object_fields.split(','):
            item_definition.add_objectitem(
                GraphQlObjectItem(
                    object_field,
                    description=object_field
                )
            )

        if base_type != 'Mutation':
            schema.add_objecttype(
                item_definition
            )
        self.add_graphqlschema('etc/schema.graphqls', schema)

        resolver_atttributes = []
        if base_type == 'Query':
            resolver_atttributes = ['private ${}DataProvider;'.format(identifier)]

        resolver = Phpclass(
            'Model\\Resolver\\{}'.format(item_identifier),
            implements=['ResolverInterface'],
            dependencies=[
                'Magento\\Framework\\Exception\\NoSuchEntityException',
                'Magento\\Framework\\GraphQl\\Config\\Element\\Field',
                'Magento\\Framework\\GraphQl\\Exception\\GraphQlInputException',
                'Magento\\Framework\\GraphQl\\Exception\\GraphQlNoSuchEntityException',
                'Magento\\Framework\\GraphQl\\Query\\ResolverInterface',
                'Magento\\Framework\\GraphQl\\Schema\\Type\\ResolveInfo',
            ],
            attributes=resolver_atttributes
        )

        resolver_construct_params = []
        resolver_construct_body = ""
        resolver_construct_docstring = []

        if base_type == 'Query':
            resolver_construct_params = [
                'DataProvider\\{} ${}DataProvider'.format(item_identifier, identifier)
            ]
            resolver_construct_body = "$this->{0}DataProvider = ${0}DataProvider;".format(identifier)
            resolver_construct_docstring = [
                '@param DataProvider\\{} ${}Repository'.format(item_identifier, identifier)
            ]

        resolver.add_method(
            Phpmethod(
                '__construct',
                params=resolver_construct_params,
                body=resolver_construct_body,
                docstring=resolver_construct_docstring
            )
        )

        resolver_resolve_body = ""
        if base_type == 'Query':
            resolver_resolve_body = """${0}Data = $this->{0}DataProvider->get{1}();
return ${0}Data;""".format(identifier, item_identifier)

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
                body=resolver_resolve_body,
                docstring=[
                    '@inheritdoc'
                ]
            )
        )

        self.add_class(resolver)

        data_provider_construct_params = []
        data_provider_attributes = []
        data_provider_construct_body = ""
        data_provider_construct_docstring = []
        if data_provider_dependency:
            data_provider_dependency_variable = "{}".format(
                lowerfirst(data_provider_dependency.split('\\')[-1]).replace('Interface', ''))
            data_provider_construct_params = [
                "{} ${}".format(data_provider_dependency, data_provider_dependency_variable)
            ]
            data_provider_construct_body = "$this->{data_provider_dependency_variable} = ${data_provider_dependency_variable};".format(
                data_provider_dependency_variable=data_provider_dependency_variable
            )
            data_provider_construct_docstring = [
                '@param {} ${}'.format(data_provider_dependency, data_provider_dependency_variable)
            ]
            data_provider_attributes = [
                'private ${};'.format(data_provider_dependency_variable)
            ]

        data_provider = Phpclass(
            'Model\\Resolver\\DataProvider\\{}'.format(item_identifier),
            dependencies=[],
            attributes=data_provider_attributes
        )

        data_provider.add_method(
            Phpmethod(
                '__construct',
                params=data_provider_construct_params,
                body=data_provider_construct_body,
                docstring=data_provider_construct_docstring
            )
        )

        data_provider.add_method(
            Phpmethod(
                'get{}'.format(item_identifier),
                params=[],
                body="return 'proviced data';",
                docstring=[]
            )
        )

        if base_type == 'Query':
            self.add_class(data_provider)

        sequence_modules = [
            Xmlnode('module', attributes={'name': 'Magento_GraphQl'})
        ]

        data_provider_dependency_splitted = data_provider_dependency.split('\\')
        if len(data_provider_dependency_splitted) > 1:
            sequence_modules.append(Xmlnode('module', attributes={
                'name': '{}_{}'.format(data_provider_dependency_splitted[0], data_provider_dependency_splitted[1])}))

        etc_module = Xmlnode('config', attributes={
            'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Module/etc/module.xsd"}, nodes=[
            Xmlnode('module', attributes={'name': self.module_name}, nodes=[
                Xmlnode('sequence', attributes={}, nodes=sequence_modules)
            ])
        ])
        self.add_xml('etc/module.xml', etc_module)

        if base_type == 'Query':

            path = os.path.join('src', 'queries')
            self.add_static_file(path, StaticFile(
                    'get{}{}.graphql'.format(upperfirst(self._module.package), item_identifier),
                    body="""query {identifier}() {{
    {identifier}() {{
        {object_fields_string}
    }}
}}""".format(
                        identifier=identifier,
                        object_fields_string="\n\t".join(object_fields.split(","))
                )
            )
            )

    @classmethod
    def params(cls):
        return [
            SnippetParam(name='base_type', choises=cls.GRAPHQL_TYPE_CHOISES, default='Query'),
            SnippetParam(
                name='custom_type', required=True,
                depend={'base_type': 'Custom'},
                description='Example: products',
                regex_validator=r'^[a-zA-Z\d\-_\s]+$',
                error_message='Only alphanumeric'
            ),
            SnippetParam(
                name='identifier', required=True,
                depend={'base_type': r'Query|Mutation'},
                description='Example: products',
                regex_validator=r'^[a-zA-Z\d\-_\s]+$',
                error_message='Only alphanumeric'
            ),
            SnippetParam(
                name='description',
                description='Short description the Query/Mutation',
                required=False
            ),
            SnippetParam(
                name='object_arguments',
                depend={'base_type': r'Query|Mutation'},
                required=False,
                description='comma seperated. Example: id',
                error_message='Only alphanumeric'
            ),
            SnippetParam(
                name='object_fields',
                required=False,
                depend={'base_type': r'Query|Custom'},
                description='comma seperated. Example: id,code,website_id,locale',
                error_message='Only alphanumeric'
            ),
            SnippetParam(
                name='data_provider_dependency',
                required=False,
                depend={'base_type': 'Query'},
                description='Example: Magento\Store\Api\StoreConfigManagerInterface',
                regex_validator=r'^[\w\\]+$',
                error_message='Only alphanumeric, underscore and backslash characters are allowed'
            ),
			 SnippetParam(
				name='add_cache_identity',
				required=True,
                depend={'base_type': 'Query'},
				default=False,
				yes_no=True),
        ]


