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
	description = """
	With observers you can hook in on events fired by Magento or other third party modules. 
	For creating an observer we need the event name and the scope:

	- **Event name:** Name of event you want to observe, example: catalog_product_save_after
	- **Scope:** For which scope the observer is active.
		- *All:* Observer is always active
		- *Frontend:* Observer is only active in the frontend of Magento.
		- *Backend:* Observer is only active in the admin panel of Magento.

	Some events:
	------------
	- sales_order_place_before
	- sales_order_place_after
	- checkout_cart_product_add_after
	- checkout_cart_update_items_before 
	- checkout_cart_save_before
	- catalog_product_get_final_price
	"""
	
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
			SnippetParam(
				name='event', 
				required=True, 
				description='Magento event name, example: catalog_product_save_after',
				regex_validator= r'^[a-zA-Z]{1}\w+$',
				error_message='Only alphanumeric and underscore characters are allowed, and need to start with a alphabetic character.'),
			SnippetParam(name='scope', choises=cls.SCOPE_CHOISES, default=cls.SCOPE_ALL)
		]
