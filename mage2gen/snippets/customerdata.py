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
from .. import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam, Readme
from ..utils import upperfirst


class CustomerSectionDataSnippet(Snippet):
    snippet_label = 'Customer(Section) Data'

    description = """Creates a Customer(Section) Data

    	Since private content is specific to individual users, it’s reasonable to handle it on the client (i.e., web browser). 
    	
    	Use our customer-data JS library to store private data in local storage, invalidate private data using customizable rules, and synchronize data with the backend. 

    	"""

    def add(self, section_class, extra_params=None):
        section_code = section_class.lower().replace(' ', '_')
        section_class = Phpclass('CustomerData\\{}'.format(upperfirst(section_class)), attributes=[
            'protected $logger;'
        ])

        section_class.add_method(Phpmethod(
            '__construct',
            params=[
                '\Psr\Log\LoggerInterface $logger',
            ],
            body="$this->logger = $logger;",
            docstring=[
                'Constructor',
                '',
                '@param \\Psr\\Log\\LoggerInterface $logger',
            ]
        ))

        section_class.add_method(Phpmethod(
            'getSectionData',
            body='return []',
            docstring=[
                '{@inheritdoc}',
            ]
        ))

        self.add_class(section_class)

        # Section XML
        section_xml = Xmlnode('config', attributes={'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance', 'xsi:noNamespaceSchemaLocation': "urn:magento:module:ObjectManager/etc/config.xsd"},
            nodes=[
                Xmlnode(
                    'type',
                        attributes={
                            'name': 'Magento\Customer\CustomerData\SectionPoolInterface'
                        },
                        nodes=[
                            Xmlnode(
                                'arguments',
                                nodes=[
                                    Xmlnode('argument', attributes={'name': 'sectionSourceMap', 'xsi:type': 'array'},
                                        nodes=[
                                            Xmlnode('item', attributes={'name': '{}-data'.format(section_code), 'xsi:type': 'string'}, node_text=section_class.class_namespace)
                                        ])
                                ])
                        ]),
            ]);

        self.add_xml('etc/frontend/di.xml', section_xml)

        self.add_static_file(
            '.',
            Readme(
                specifications=" - Customer Data Section\n\t- {}".format(section_code),
            )
        )


    @classmethod
    def params(cls):
        return [
            SnippetParam(
                name='section_class',
                required=True,
                description='Customer(Section) Data Class',
                regex_validator=r'^[a-zA-Z]{1}[a-zA-Z]+$',
                error_message='Only alphanumeric are allowed, and need to start with a alphabetic character.'
            ),
        ]
