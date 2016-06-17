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
import os

from mage2gen import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam
from mage2gen.utils import upperfirst


class ObserverSnippet(Snippet):
	SCOPE_ALL = 'all'
	SCOPE_FRONTEND = 'frontend'
	SCOPE_ADMINHTML = 'backend'

	SCOPE_CHOISES = [
		(SCOPE_ALL, 'All'),
		(SCOPE_FRONTEND, 'Frontend'),
		(SCOPE_ADMINHTML, 'Backend'),
	]
	
	def add(self, event, scope=SCOPE_ALL):
		split_event = event.split('_')

		observer = Phpclass(
			'\\'.join(['Observer', split_event[0], ''.join(upperfirst(item) for item in split_event[1:])]),
			implements=['\Magento\Framework\Event\ObserverInterface'])
		observer.add_method(Phpmethod(
			'execute',
			params=['\Magento\Framework\Event\Observer $observer']
		))

		self.add_class(observer)	

		config = Xmlnode('config', attributes={'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance','xsi:noNamespaceSchemaLocation':"urn:magento:framework:Event/etc/events.xsd"}, nodes=[
			Xmlnode('event', attributes={'name': event}, nodes=[
				Xmlnode('observer', attributes={
					'name': '{}_{}'.format(observer.class_namespace.replace('\\', '_').lower(), event),
					'instance':observer.class_namespace,
				})
			])
		])

		xml_path = ['etc']
		if scope == self.SCOPE_FRONTEND:
			xml_path.append('frontend')
		elif scope == self.SCOPE_ADMINHTML:
			xml_path.append('adminhtml')

		xml_path.append('events.xml')


		self.add_xml(os.path.join(*xml_path), config)

	@classmethod
	def params(cls):
		return [
			SnippetParam(name='event', required=True),
			SnippetParam(name='scope', choises=cls.SCOPE_CHOISES, default=cls.SCOPE_ALL)
		]
