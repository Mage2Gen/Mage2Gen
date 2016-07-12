import os, locale
from mage2gen import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam

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

	def add(self, cronjob_name, schedule='*/5 * * * *'):

		crontab_file = 'etc/crontab.xml'

		instance = "Magento\Sales\Cron\CleanExpiredQuotes"

		class_name_parts = []
		for cronjob_name_part in cronjob_name.split(' '):
			class_name_parts.append(cronjob_name_part.capitalize())

		class_name = ''.join(class_name_parts)

		method= "execute"

		crontab_class = Phpclass('Cron\\'+class_name)
		crontab_class.attributes.append('protected $logger;')
		crontab_class.add_method(Phpmethod(
            '__construct',
            params=[
                '\Psr\Log\LoggerInterface $logger',
            ],
            body="$this->logger = $logger;"
        ))
		crontab_class.add_method(Phpmethod('execute',body='$this->logger->addInfo("Cronjob '+cronjob_name+' is executed.");'))
	
		self.add_class(crontab_class)

		cronjob_name = (self.module_name + '_' + cronjob_name).lower().replace(' ','_')

		crontab_xml = Xmlnode('config',attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Cron:etc/crontab.xsd"},nodes=[
			Xmlnode('group',attributes={'id':'default'},nodes=[
				Xmlnode(
					'job',
					attributes={
						'name':cronjob_name,
						'instance': crontab_class.class_namespace,
						'method': method,
					}, 
					nodes=[
						Xmlnode('schedule',node_text=schedule)
					]
				)	
			])
		]);

		self.add_xml(crontab_file, crontab_xml)

	@classmethod
	def params(cls):
		return [
			SnippetParam(
                name='cronjob_name', 
                required=True, 
                description='Cronjob Name',
                regex_validator= r'^[a-zA-Z]{1}\w+$',
                error_message='Only alphanumeric and underscore characters are allowed, and need to start with a alphabetic character.'),
			SnippetParam(
                name='schedule', 
                required=True, 
                default='*/5 * * * *',
                description='Cron Schedule. For example */5 * * * *',
                regex_validator= r'^([\d*,-/]+)\s+([\d*,-/]+)\s+([\d*,-/\?LW]+)\s+([\d\w*,-/]+)\s+([\d\w*,-/\?L#]+)\s*([\d\w*,-/]*)$',
                error_message='Enter a valid cron schedule'),
		]
