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
from mage2gen import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet

class InstallSnippet(Snippet):
	description = """
	Install is used for creating database tables and adding data to Magento 2. It uses Schema and Data install and upgrade classes.

	- **from_version:** Add sample upgrade from version statement

	Snippet generation
	------------------
	When you generate a module, the following classes will be created:

	**Install scripts**
	
	- Setup/InstallSchema
	- Setup/InstallData

	**Upgrade scripts** (With the sample from_version statement)
	
	- Setup/UpgradeSchema
	- Setup/UpgradeData  
	"""

	def add(self,from_version='1.0.0'):

		install_schema = Phpclass('Setup\\InstallSchema',implements=['InstallSchemaInterface'],dependencies=['Magento\\Framework\\Setup\\InstallSchemaInterface','Magento\\Framework\\Setup\\ModuleContextInterface','Magento\\Framework\\Setup\\SchemaSetupInterface'])
		install_schema.add_method(Phpmethod('install',params=['SchemaSetupInterface $setup','ModuleContextInterface $context'],body='$installer = $setup;\n $installer->startSetup();\n $installer->endSetup();'))
	
		self.add_class(install_schema)

		install_data = Phpclass('Setup\\InstallData',implements=['InstallDataInterface'],dependencies=['Magento\\Framework\\Setup\\InstallDataInterface','Magento\\Framework\\Setup\\ModuleContextInterface','Magento\\Framework\\Setup\\ModuleDataSetupInterface'])
		install_data.add_method(Phpmethod('install',params=['ModuleDataSetupInterface $setup','ModuleContextInterface $context']))
	
		self.add_class(install_data)

		update_schema = Phpclass('Setup\\UpgradeSchema',implements=['UpgradeSchemaInterface'],dependencies=['Magento\\Framework\\Setup\\UpgradeSchemaInterface','Magento\\Framework\\Setup\\ModuleContextInterface','Magento\\Framework\\Setup\\SchemaSetupInterface'])
		update_schema.add_method(Phpmethod('upgrade',params=['SchemaSetupInterface $setup','ModuleContextInterface $context'],body='$setup->startSetup();\nif(version_compare($context->getVersion(), "'+from_version+'", "<")){\n//Your upgrade script\n}\n$setup->endSetup();\n'))
	
		self.add_class(update_schema)

		update_data = Phpclass('Setup\\UpgradeData',implements=['UpgradeDataInterface'],dependencies=['Magento\\Framework\\Setup\\UpgradeDataInterface','Magento\\Framework\\Setup\\ModuleContextInterface','Magento\\Framework\\Setup\\ModuleDataSetupInterface'])
		update_data.add_method(Phpmethod('upgrade',params=['ModuleDataSetupInterface $setup','ModuleContextInterface $context'],body='$setup->startSetup();\nif(version_compare($context->getVersion(), "'+from_version+'", "<")){\n//Your upgrade script\n}\n$setup->endSetup();\n'))
		
		self.add_class(update_data)		
