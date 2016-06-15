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

	def add(self):

		install_schema = Phpclass('Setup\\InstallSchema',implements=['InstallSchemaInterface'],dependencies=['Magento\Eav\Setup\EavSetup','Magento\Eav\Setup\EavSetupFactory','Magento\Framework\Setup\InstallSchemaInterface','Magento\Framework\Setup\ModuleContextInterface','Magento\Framework\Setup\SchemaSetupInterface','Magento\Framework\DB\Adapter\AdapterInterface'])
		install_schema.add_method(Phpmethod('install',params=['SchemaSetupInterface $setup','ModuleContextInterface $context'],body='$installer = $setup;\n $installer->startSetup();\n $installer->endSetup();'))
	
		self.add_class(install_schema)

		install_data = Phpclass('Setup\\InstallData',implements=['InstallDataInterface'])
	
		self.add_class(install_data)

		update_schema = Phpclass('Setup\\UpgradeSchema',implements=['UpgradeSchemaInterface'])
	
		self.add_class(update_schema)

		update_data = Phpclass('Setup\\UpgradeData',implements=['UpgradeDataInterface'])
	
		self.add_class(update_data)		
