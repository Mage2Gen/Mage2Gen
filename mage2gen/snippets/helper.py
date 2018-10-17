# A Magento 2 module generator library
# Copyright (C) 2018 Derrick Heesbeen
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
from .. import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam

class HelperSnippet(Snippet):
	snippet_label = 'Helper'
	
	description = """
	A Helper can be used to retrieve logic which can be used more then once. For example the module function isEnabled.
	"""

	def add(self,helper_name, add_enabled_function, extra_params=None):

		helper = Phpclass(
			'Helper\\'+helper_name, 
			extends='AbstractHelper',
			dependencies = [
			'Magento\Framework\App\Helper\AbstractHelper'
			],
			attributes = [
			]
		)

		helper.add_method(
			Phpmethod(
				'__construct',
				params=[
					'\\Magento\\Framework\\App\\Helper\\Context $context'
				],
				body="""
					parent::__construct($context);
					""",
				docstring=['@param \Magento\Framework\App\Helper\Context $context']
			)
		)

		if add_enabled_function:
			helper.add_method(
				Phpmethod(
				'isEnabled',
				body="""
				return true;
				""",
				docstring=['@return bool']
				)
			)

		self.add_class(helper)

	@classmethod
	def params(cls):
		return [
			SnippetParam(
				name='helper_name', 
				required=True, 
				description='Example: Backup, Import',
				regex_validator= r'^[a-zA-Z]{1}\w+$',
				error_message='Only alphanumeric and underscore characters are allowed, and need to start with a alphabetic character.'
			),
			SnippetParam(name='add_enabled_function', yes_no=True),
		]


