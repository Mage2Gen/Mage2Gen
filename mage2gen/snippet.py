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
class Snippet:

	def __init__(self, module):
		self._module = module

	@property
	def module_name(self):
	    return self._module.module_name

	def add_class(self, phpclass):
		return self._module.add_class(phpclass)

	def add_xml(self, xml_file, node):
		return self._module.add_xml(xml_file, node)

	def add_static_file(self, path, staticfile):
		return self._module.add_static_file(path, staticfile)

	def add(self, *args, **kwargs):
		raise Exception('Not implemented')