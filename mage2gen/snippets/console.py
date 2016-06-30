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
import os
from mage2gen import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam

class ConsoleSnippet(Snippet):
	description = """
	Console commands are listed and executed by **bin/magento** command line tool.

	- **action_name:** Console action name. Example: Backup, Import
	- **short_description:** Console action description. Example: Backups the Magento environment, Starts product import

	Snippet generation
	------------------
	When you generate a module with an action_name (*backup*) and the module is named (*MageGen/Module*).
	The generated command used by **bin/magento** is:
	
		bin/magento mage2gen_module:backup
	"""

	def add(self,action_name,short_description):

		console = Phpclass(
			'Console\\Command\\'+action_name, 
			extends='Command',
			dependencies = [
			'Symfony\Component\Console\Command\Command',
			'Symfony\Component\Console\Input\InputArgument',
			'Symfony\Component\Console\Input\InputOption',
			'Symfony\Component\Console\Input\InputInterface',
			'Symfony\Component\Console\Output\OutputInterface'
			],
			attributes = ['const NAME_ARGUMENT = "name";','const NAME_OPTION = "option";']
		)

		console.add_method(
			Phpmethod(
			'execute',
			access='protected',
			params=['InputInterface $input','OutputInterface $output'],
			body='$name = $input->getArgument(self::NAME_ARGUMENT); $option = $input->getOption(self::NAME_OPTION);\n$output->writeln("Hello " . $name);'
			)
		)

		console.add_method(
			Phpmethod(
				'configure',
				access='protected',
				body='$this->setName("'+self.module_name.lower()+':'+action_name.lower()+'");\n$this->setDescription("'+short_description+'");\n$this->setDefinition([new InputArgument(self::NAME_ARGUMENT,InputArgument::OPTIONAL,"Name"),new InputOption(self::NAME_OPTION,"-a",InputOption::VALUE_NONE,"Option functionality")]);\nparent::configure();'
			)
		)

		self.add_class(console);

		config = Xmlnode('config', attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:framework:ObjectManager/etc/config.xsd"}, nodes=[
			Xmlnode('type', attributes={'name': 'Magento\Framework\Console\CommandList'}, nodes=[
				Xmlnode('arguments', nodes=[
					Xmlnode('argument', 
							attributes={
								'name':'commands',
								'xsi:type':'array',
							},
							nodes=[
								Xmlnode('item',
									attributes={
										'name':action_name,
										'xsi:type':'object'
									},
									node_text=console.class_namespace
								)
							])
				])
			])
		])

		self.add_xml('etc/di.xml', config)

	@classmethod
	def params(cls):
		return [
			SnippetParam(
				name='action_name', 
				required=True, 
				description='Console action name. Example: Backup, Import',
				regex_validator= r'^[a-zA-Z]{1}\w+$',
				error_message='Only alphanumeric and underscore characters are allowed, and need to start with a alphabetic character.'),
			SnippetParam(
				name='short_description', 
				required=True, 
				description='Console action description. Example: Backups magento enviroment, Starts product import'),
		]


