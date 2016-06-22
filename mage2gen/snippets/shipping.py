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
from mage2gen.module import TEMPLATE_DIR

class ShippingClass(Phpclass):

	template_file = os.path.join(TEMPLATE_DIR,'shipping.tmpl')

	def __init__(self, *args, shipping_code=None, **kwargs):
		super().__init__(*args, **kwargs)
		self.shipping_code = shipping_code

	def context_data(self):

		data = super().context_data()

		data['shipping_code'] = self.shipping_code

		return data 

class ShippingSnippet(Snippet):

	description = "Creates a shipping method"

	def add(self,method_name):

		system_file = 'etc/adminhtml/system.xml'
		shipping_code = method_name.lower().replace(' ', '_')
		shipping_filename = method_name.replace(' ','')

		shipping_class = ShippingClass('Model\\Carrier\\'+shipping_filename,shipping_code=shipping_code)

		self.add_class(shipping_class)

		system = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Config:etc/system_file.xsd"}, nodes=[
				Xmlnode('system',  nodes=[
					Xmlnode('section',attributes={'id':'carriers','sortOrder':1000,'showInWebsite':1,'showInStore':1,'showInDefault':1,'translate':'label'},match_attributes={'id'},nodes=[
						Xmlnode('group', attributes={'id':shipping_code,'sortOrder':10,'showInWebsite':1,'showInStore':1,'showInDefault':1,'translate':'label'},match_attributes={'id'},nodes=[
							Xmlnode('label',node_text=method_name),
							Xmlnode('field', attributes={'id':'active','type':'select','sortOrder':10,'showInWebsite':1,'showInStore':1,'showInDefault':1,'translate':'label'},match_attributes={'id'},nodes=[
								Xmlnode('label',node_text='Enabled'),
								Xmlnode('source_model',node_text='Magento\Config\Model\Config\Source\Yesno'),
							]),
							Xmlnode('field', attributes={'id':'name','type':'text','sortOrder':20,'showInWebsite':1,'showInStore':1,'showInDefault':1,'translate':'label'},match_attributes={'id'},nodes=[
								Xmlnode('label',node_text='Method Name'),
							]),
							Xmlnode('field', attributes={'id':'price','type':'text','sortOrder':30,'showInWebsite':1,'showInStore':1,'showInDefault':1,'translate':'label'},match_attributes={'id'},nodes=[
								Xmlnode('label',node_text='Price'),
								Xmlnode('validate',node_text='validate-number validate-zero-or-greater'),
							]),
							Xmlnode('field', attributes={'id':'sort_order','type':'text','sortOrder':40,'showInWebsite':1,'showInStore':1,'showInDefault':1,'translate':'label'},match_attributes={'id'},nodes=[
								Xmlnode('label',node_text='Sort Order'),
							]),
							Xmlnode('field', attributes={'id':'title','type':'text','sortOrder':50,'showInWebsite':1,'showInStore':1,'showInDefault':1,'translate':'label'},match_attributes={'id'},nodes=[
								Xmlnode('label',node_text='Title'),
							]),
							Xmlnode('field', attributes={'id':'sallowspecific','type':'select','sortOrder':60,'showInWebsite':1,'showInStore':1,'showInDefault':1,'translate':'label'},match_attributes={'id'},nodes=[
								Xmlnode('label',node_text='Ship to Applicable Countries'),
								Xmlnode('frontend_class',node_text='shipping-applicable-country'),
								Xmlnode('source_model',node_text='Magento\Shipping\Model\Config\Source\Allspecificcountries'),
							]),
							Xmlnode('field', attributes={'id':'specificcountry','type':'select','sortOrder':70,'showInWebsite':1,'showInStore':1,'showInDefault':1,'translate':'label'},match_attributes={'id'},nodes=[
								Xmlnode('label',node_text='Ship to Specific Countries'),
								Xmlnode('can_be_empty',node_text='1'),
								Xmlnode('source_model',node_text='Magento\Directory\Model\Config\Source\Country'),
							]),
							Xmlnode('field', attributes={'id':'specificerrmsg','type':'textarea','sortOrder':80,'showInWebsite':1,'showInStore':1,'showInDefault':1,'translate':'label'},match_attributes={'id'},nodes=[
								Xmlnode('label',node_text='Displayed Error Message'),
							]),
						])	
					])
				])
		])

		self.add_xml(system_file,system)

		config_file = 'etc/config.xml'

		config = Xmlnode('config',attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Store:etc/config.xsd"},nodes=[
			Xmlnode('default',nodes=[
				Xmlnode('carriers',nodes=[
					Xmlnode(shipping_code,nodes=[
						Xmlnode('model',node_text=shipping_class.class_namespace),
						Xmlnode('active',node_text='0'),
						Xmlnode('title',node_text=method_name),
						Xmlnode('name',node_text=method_name),
						Xmlnode('price',node_text='0.00'),
						Xmlnode('specificerrmsg',node_text='This shipping method is not available. To use this shipping method, please contact us.'),
						Xmlnode('sallowspecific',node_text='0'),
					])
				])
			])
		]);

		self.add_xml(config_file, config)

	@classmethod
	def params(cls):
		return [
			SnippetParam(
				name='method_name', 
				required=True, 
				description='Shipping Method name. Example: Freeshipping, Per product shipping',
				regex_validator= r'^[a-z\d\-_\s]+$',
				error_message='Only alphanumeric'),
		]
