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
import os, locale
from collections import OrderedDict
from mage2gen import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam


class ModelSnippet(Snippet):
	FIELD_TYPE_CHOISES = [
		('boolean','Boolean'),	
		('smallint','Smallint'),	
		('integer','Integer'),
		('bigint', 'Bigint'),
		('float', 'Float'),
		('numeric', 'Numeric'),
		('decimal', 'Decimal'),
		('date', 'Date'),
		('timestamp', 'Timestamp'),
		('datatime', 'Datetime'),
		('text', 'Text'),
		('blob', 'Blob'),
	]

	def add(self, model_name, field_name, field_type, extra_params=False):
		model_id = '{}_id'.format(model_name.lower())
		install_class = Phpclass('Setup\\InstallSchema',implements=['InstallSchemaInterface'],dependencies=[
			'Magento\\Framework\\Setup\\InstallSchemaInterface',
			'Magento\\Framework\\Setup\\ModuleContextInterface',
			'Magento\\Framework\\Setup\\SchemaSetupInterface'])

		# Start setup
		install_method = Phpmethod('install', params=['SchemaSetupInterface $setup','ModuleContextInterface $context'],
			body='$installer = $setup;\n$installer->startSetup();',
			body_return='$setup->endSetup();')
		
		# Create table
		install_method.body.append("$table{0} = $setup->getConnection()->newTable($setup->getTable('{0}'));".format(model_name))
		
		# add model id field
		install_method.body.append("$table{table}->addColumn(\n  '{field}',\n  {type},\n  {size},\n  {options},\n  '{comment}'\n);".format(
			table=model_name,
			field=model_id,
			type='\\Magento\\Framework\\DB\\Ddl\\Table::TYPE_INTEGER',
			size='null',
			options="array('identity' => true,'nullable' => false,'primary' => true,'unsigned' => true,)",
			comment='Entity ID'	
		))

		# create options
		options = OrderedDict()
		if extra_params.get('default'):
			options['default'] = "'{}'".format(extra_params.get('default'))
		if not extra_params.get('nullable'):
			options['nullable'] = extra_params.get('nullable')
		if extra_params.get('primary'):
			options['primary'] = extra_params.get('primary')
		if extra_params.get('primary_position'):
			options['primary_position'] = extra_params.get('primary_position')
		if extra_params.get('identity'):
			options['identity'] = True
		if extra_params.get('auto_increment'):
			options['auto_increment'] = True
		if extra_params.get('unsigned'):
			options['unsigned'] = True
		if extra_params.get('precision'):
			options['precision'] = extra_params.get('precision')
		if extra_params.get('scale'):
			options['scale'] = extra_params.get('scale')
		
		options = "[{}]".format(','.join("'{}' => {}".format(key, value) for key, value in options.items()))

		# Add field
		install_method.body.append("$table{table}->addColumn(\n  '{field}',\n  {type},\n  {size},\n  {options},\n  '{comment}'\n);".format(
			table=model_name,
			field=field_name,
			type='\\Magento\\Framework\\DB\\Ddl\\Table::TYPE_{}'.format(field_type.upper()),
			size=extra_params.get('field_size') or 'null',
			options=options,
			comment=extra_params.get('comment') or field_name	
		))
		
		# End setup + create table 
		install_method.end_body.append('$setup->getConnection()->createTable($table{});'.format(model_name))

		install_class.add_method(install_method)
		self.add_class(install_class)
		
		# Create resource class
		resource_model_class = Phpclass('Model\\ResourceModel\\' + model_name.replace('_', '\\'), extends='\\Magento\\Framework\\Model\\ResourceModel\\Db\\AbstractDb')
		resource_model_class.add_method(Phpmethod('_construct', access=Phpmethod.PROTECTED, body="$this->_init('{}', '{}');".format(model_name, model_id)))
		self.add_class(resource_model_class)

		# Create model class
		model_class = Phpclass('Model\\' + model_name.replace('_', '\\'), extends='\\Magento\\Framework\\Model\\AbstractModel')
		model_class.add_method(Phpmethod('_construct', access=Phpmethod.PROTECTED, body="$this->_init('{}');".format(resource_model_class.class_namespace)))
		self.add_class(model_class)

		# Create collection
		collection_model_class = Phpclass('Model\\ResourceModel\\' + model_name.replace('_', '\\') + '\\Collection', extends='\\Magento\\Framework\\Model\\ResourceModel\\Db\\Collection\\AbstractCollection')
		collection_model_class.add_method(Phpmethod('_construct', access=Phpmethod.PROTECTED, body="$this->_init(\n  '{}',\n  '{}');".format(
			model_class.class_namespace ,resource_model_class.class_namespace)))
		self.add_class(collection_model_class)

	@classmethod
	def params(cls):
		return [
			SnippetParam(
				name='model_name', 
				required=True, 
				regex_validator= r'^[a-zA-Z]{1}\w+$',
				error_message='Only alphanumeric and underscore characters are allowed, and need to start with a alphabetic character.'
			),
			SnippetParam(
				name='field_name', 
				required=True, 
				regex_validator= r'^[a-zA-Z]{1}\w+$',
				error_message='Only alphanumeric and underscore characters are allowed, and need to start with a alphabetic character.'
			),
			SnippetParam(
				name='field_type', 
				choises=cls.FIELD_TYPE_CHOISES, 
				default='text',
			),
		]

	@classmethod
	def extra_params(cls):
		return [
			SnippetParam('comment', required=False),
			SnippetParam('default', required=False),
			SnippetParam(
				name='primary_position',
				required=False, 
				regex_validator= r'^\d+$',
				error_message='Only numeric value allowed.',

			),
			SnippetParam('primary', yes_no=True),
			SnippetParam('nullable', yes_no=True, default=True),
			SnippetParam('identity', yes_no=True),
			SnippetParam('auto_increment', yes_no=True),
			'Extra',
			SnippetParam(
				name='field_size', 
				required=False, 
				regex_validator= r'^\d+$',
				error_message='Only numeric value allowed.',
				depend={'field_type': r'text|blob|decimal|numeric'}
			),
			SnippetParam(
				name='precision', 
				required=False, 
				regex_validator= r'^\d+$',
				error_message='Only numeric value allowed.',
				depend={'field_type': r'decimal|numeric'}
			),
			SnippetParam(
				name='scale', 
				required=False, 
				regex_validator= r'^\d+$',
				error_message='Only numeric value allowed.',
				depend={'field_type': r'decimal|numeric'}
			),
			SnippetParam(
				name='unsigned', 
				yes_no=True, 
				depend={'field_type': r'smallint|integer|bigint|float|decimal|numeric'}
			),


		]


