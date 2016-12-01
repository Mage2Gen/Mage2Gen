
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
from mage2gen import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam
from mage2gen.utils import upperfirst

class CronjobSnippet(Snippet):

	description ="""
		
		With this snippet you can create a class with a 'excute' method wich will be executed by the magento cron schedule according to the cron schedule you have configured.

		The class will be created within the "Cron" folder of the module. 

		To build up the cron schedule manually use php bin/magento cron:run		

		You should find a log in the var/log/system.log after the cronjob has runned. 

		In the Magento 2 Adminpanel under Stores > Configuration > Advanched > System you change scheduler settings per cron group. 

		You can create your own groups if you wish. In that case be sure to add extra system settings. 

		Instead of the <schedule> tag in the crontab.xml you can set a system config path 

		Example

		 <config_path>crontab/default/jobs/catalog_product_alert/schedule/cron_expr</config_path> 

		This way a admin user can configure the cronschedule for this task.

    """

	def add(self, cronjob_class, schedule='*/5 * * * *', extra_params=None):

		crontab_class = Phpclass('Cron\\{}'.format(upperfirst(cronjob_class)), attributes=[
			'protected $logger;'
		])

		crontab_class.add_method(Phpmethod(
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
		crontab_class.add_method(Phpmethod('execute',
			body='$this->logger->addInfo("Cronjob '+cronjob_class+' is executed.");',
			docstring=[
            	'Execute the cron',
            	'',
            	'@return void',
            ]
		))
	
		self.add_class(crontab_class)

		crontab_xml = Xmlnode('config',attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Cron:etc/crontab.xsd"},nodes=[
			Xmlnode('group',attributes={'id':'default'},nodes=[
				Xmlnode(
					'job',
					attributes={
						'name': "{}_{}".format(self.module_name, cronjob_class).lower(),
						'instance': crontab_class.class_namespace,
						'method': "execute",
					}, 
					nodes=[
						Xmlnode('schedule',node_text=schedule)
					]
				)	
			])
		]);

		self.add_xml('etc/crontab.xml', crontab_xml)

	@classmethod
	def params(cls):
		return [
			SnippetParam(
                name='cronjob_class', 
                required=True, 
                description='Cronjob class',
                regex_validator= r'^[a-zA-Z]{1}[a-zA-Z]+$',
                error_message='Only alphanumeric are allowed, and need to start with a alphabetic character.'),
			SnippetParam(
                name='schedule', 
                required=True, 
                default='*/5 * * * *',
                description='Cron Schedule. For example */5 * * * *',
                regex_validator= r'^([\d*,-/]+)\s+([\d*,-/]+)\s+([\d*,-/\?LW]+)\s+([\d\w*,-/]+)\s+([\d\w*,-/\?L#]+)\s*([\d\w*,-/]*)$',
                error_message='Enter a valid cron schedule'),
		]
