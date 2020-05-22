# Copyright © Experius All rights reserved.
# See COPYING.txt for license details.

from .. import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam, Readme
from ..utils import upperfirst

class CronjobSnippet(Snippet):

	description ="""
		
		With this snippet you can create a class with a 'execute' method wich will be executed by the magento cron schedule according to the cron schedule you have configured.

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

	def add(self, cronjob_class, schedule='*/5 * * * *', cronjob_group='default', extra_params=None):

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
			Xmlnode('group', attributes={'id': cronjob_group.lower()},nodes=[
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

		self.add_static_file(
			'.',
			Readme(
				specifications=" - Cronjob\n\t- {}".format("{}_{}".format(self.module_name, cronjob_class).lower()),
			)
		)

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
				name='cronjob_group',
				required=True,
				default='default',
				description='Cronjob Group',
				regex_validator=r'^[a-zA-Z]{1}[a-zA-Z]+$',
				error_message='Only alphanumeric are allowed, and need to start with a alphabetic character.'),
			SnippetParam(
                name='schedule', 
                required=True, 
                default='*/5 * * * *',
                description='Cron Schedule. For example */5 * * * *',
                regex_validator= r'^([\d*,-/]+)\s+([\d*,-/]+)\s+([\d*,-/\?LW]+)\s+([\d\w*,-/]+)\s+([\d\w*,-/\?L#]+)\s*([\d\w*,-/]*)$',
                error_message='Enter a valid cron schedule'),
		]
