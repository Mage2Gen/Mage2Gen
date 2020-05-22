# Copyright © Experius All rights reserved.
# See COPYING.txt for license details.

import os, locale
from .. import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam, Readme
from ..utils import upperfirst


class SalesAttributeSnippet(Snippet):
    snippet_label = 'Sales Attribute'

    FRONTEND_INPUT_TYPE = [
        ("text", "Text Field"),
        ("textarea", "Text Area"),
        ("date", "Date"),
        # ("boolean", "Yes/No"),
        # ("multiselect", "Multiple Select"),
        # ("select", "Dropdown"),
    ]

    FRONTEND_INPUT_VALUE_TYPE = {
        "text": "varchar",
        "textarea": "text",
        "date": "date",
        "boolean": "int",
        "multiselect": "varchar",
        "select": "int",
    }

    SALES_ENTITIES = [
        ("quote", "Quote"),
        ("quote_item", "Quote Item"),
        ("quote_address", "Quote Address"),
        # ("quote_address_item", "Quote Address Item"),
        # ("quote_address_rate", "Quote Address Rate"),
        ("sales_order", "Order"),
        # ("sales_order_payment", "Order Payment"),
        ("sales_order_item", "Order Item"),
        ("sales_order_address", "Order Address"),
        # ("order_status_history", "Order Status History"),
        ("sales_invoice", "Invoice"),
        ("sales_invoice_item", "Invoice Item"),
        # ("sales_invoice_comment", "Invoice Comment"),
        ("sales_creditmemo", "Creditmemo"),
        ("sales_creditmemo_item", "Creditmemo Item"),
        # ("sales_creditmemo_comment", "Creditmemo Comment"),
        ("sales_shipment", "Shipment"),
        ("sales_shipment_item", "Shipment Item"),
        # ("sales_shipment_track", "Shipment Track"),
        # ("sales_shipment_comment", "Shipment Comment"),
    ]

    description = """
		Install Magento 2 sales order attributes programmatically.
	"""

    def add(self, attribute_label, sales_entity='quote', frontend_input='varchar', required=False, upgrade_data=False,
            from_version='1.0.1', extra_params=None):
        extra_params = extra_params if extra_params else {}
        value_type = self.FRONTEND_INPUT_VALUE_TYPE.get(frontend_input)

        attribute_code = extra_params.get('attribute_code', None)
        if not attribute_code:
            attribute_code = attribute_label.lower().replace(' ', '_')[:30]

        if extra_params.get('field_size'):
            size = extra_params.get('field_size')
        elif value_type == 'decimal':
            size = '\'12,4\''
        elif value_type == 'varchar' and not extra_params.get('field_size'):
            size = '255'
        else:
            size = 'null'

        templatePath = os.path.join(os.path.dirname(__file__), '../templates/attributes/sales/attribute.tmpl')

        with open(templatePath, 'rb') as tmpl:
            template = tmpl.read().decode('utf-8')

        attributes = {
            'name': "{}".format(attribute_code),
            'nullable': "true",
            'xsi:type': value_type,
            'comment': attribute_label
        }
        if size:
            attributes['length'] = size
        if value_type == 'integer' or value_type == 'bigint':
            attributes['xsi:type'] = "int"
        elif value_type == 'numeric':
            attributes['xsi:type'] = "real"

        if extra_params.get('default'):
            attributes['default'] = "{}".format(extra_params.get('default'))
        if not extra_params.get('nullable'):
            attributes['nullable'] = 'false'
            required = not attributes['nullable']
        if value_type in {'mallint', 'integer', 'bigint'}:
            attributes['identity'] = 'false'
            if extra_params.get('identity'):
                attributes['identity'] = 'true'
        if extra_params.get('unsigned'):
            attributes['unsigned'] = 'true'
        if extra_params.get('precision'):
            attributes['precision'] = extra_params.get('precision')
        if extra_params.get('scale'):
            attributes['scale'] = extra_params.get('scale')
        if extra_params.get('field_size'):
            attributes['length'] = '{}'.format(extra_params.get('field_size'))
        elif value_type == 'decimal':
            attributes['scale'] = '4'
            attributes['precision'] = '12'
        elif value_type == 'varchar' and not extra_params.get('field_size'):
            attributes['length'] = '255'

        # Create db_schema.xml declaration

        db_nodes = [
            Xmlnode('table', attributes={
                'name': "{}".format(sales_entity),
            }, nodes=[
                Xmlnode('column', attributes=attributes)
            ])
        ]
        if extra_params.get('used_in_admin_grid') and not sales_entity.__contains__('quote'):
            virtual_types = {
                "sales_order": "Magento\\Sales\\Model\\ResourceModel\\Order\Grid",
                "sales_invoice": "Magento\\Sales\\Model\\ResourceModel\\Order\\Invoice\\Grid",
                "sales_shipment": "ShipmentGridAggregator",
                "sales_creditmemo": "CreditmemoGridAggregator",
            }

            if sales_entity in virtual_types:
                db_nodes.append(Xmlnode('table', attributes={
                    'name': "{}_grid".format(sales_entity),
                }, nodes=[
                    Xmlnode('column', attributes=attributes)
                ]))
                self.add_xml('etc/di.xml', Xmlnode('schema', attributes={
                    'xsi:noNamespaceSchemaLocation': "urn:magento:framework:ObjectManager/etc/config.xsd"},
                              nodes=[
                                  Xmlnode('virtualType', attributes={
                                      'name': virtual_types[sales_entity],
                                      'type': 'Magento\\Sales\\Model\\ResourceModel\\Grid',
                                  }, nodes=[
                                      Xmlnode('arguments', attributes={}, nodes=[
                                          Xmlnode('argument', attributes={'name': 'columns', 'xsi:type': 'array'}, nodes=[
                                              Xmlnode('item', attributes={'name': ''.format(attribute_code), 'xsi:type': 'string'}, 
                                                      node_text="{}.{}".format(sales_entity, attribute_code)
                                                      )
                                          ])
                                      ])
                                  ])
                  ]))


        self.add_xml('etc/db_schema.xml', Xmlnode('schema', attributes={
            'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Setup/Declaration/Schema/etc/schema.xsd"},
                                                  nodes=db_nodes))


        etc_module = Xmlnode('config', attributes={
            'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Module/etc/module.xsd"}, nodes=[
            Xmlnode('module', attributes={'name': self.module_name}, nodes=[
                Xmlnode('sequence', attributes={}, nodes=[
                    Xmlnode('module', attributes={'name': 'Magento_Sales'})
                ])
            ])
        ])
        self.add_xml('etc/module.xml', etc_module)

        self.add_static_file(
            '.',
            Readme(
                attributes=" - Sales - {} ({})".format(attribute_label, attribute_code),
            )
        )

    @classmethod
    def params(cls):
        return [
            SnippetParam(
                name='sales_entity',
                choises=cls.SALES_ENTITIES,
                required=True,
                default='quote',
                repeat=True),
            SnippetParam(
                name='attribute_label',
                required=True,
                description='Example: Order Comment',
                regex_validator=r'^[a-zA-Z\d\-_\s]+$',
                error_message='Only alphanumeric',
                repeat=True),
            SnippetParam(
                name='frontend_input',
                choises=cls.FRONTEND_INPUT_TYPE,
                required=True,
                default='text',
                repeat=True),
            SnippetParam(
                name='required',
                required=True,
                default=False,
                yes_no=True,
                repeat=True),
            SnippetParam(
                name='upgrade_data',
                default=False,
                yes_no=True,
                repeat=True
            ),
            SnippetParam(
                name='from_version',
                description='1.0.1',
                default='1.0.1',
                repeat=True
            ),
        ]

    @classmethod
    def extra_params(cls):
        return [
            SnippetParam(
                name='attribute_code',
                description='Default to lowercase of label',
                regex_validator=r'^[a-zA-Z]{1}\w{0,29}$',
                error_message='Only alphanumeric and underscore characters are allowed, and need to start with a alphabetic character. And can\'t be longer then 30 characters',
                repeat=True),
            SnippetParam(
                name='field_size',
                description='Size of field, Example: 512 for max chars',
                required=False,
                regex_validator=r'^\d+$',
                error_message='Only numeric value allowed.',
                depend={'frontend_input': r'text|blob|decimal|numeric', },
                repeat=True
            ),
            SnippetParam(
                name='used_in_admin_grid',
                required=True,
                default=False,
                yes_no=True,
                depend={'sales_entity': r'sales_order$|sales_invoice|sales_shipment$|sales_creditmemo$', },
                repeat=True),
            SnippetParam(
                name='visible',
                required=True,
                default=False,
                yes_no=True,
                repeat=True),
        ]
