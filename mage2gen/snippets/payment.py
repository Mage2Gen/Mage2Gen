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

class PaymentSnippet(Snippet):

	description = """Creates a payment method

	Generated Payment methods can be found in *Magento Adminpanel > Stores > Settings > Configuration > Sales > Payment Methods*

	It allows you to add extra payment methods to Magento. For example if you need to have a payment method which can only be used in the backend 
	or if you need a payment that directly creates an invoice.

	"""

	def add(self,method_name):

		payment_code = method_name.lower().replace(' ', '_')
		payment_class_name = method_name

		payment_class = Phpclass('Model\\Payment\\'+payment_class_name,extends='\Magento\Payment\Model\Method\AbstractMethod',attributes=['protected $_code = "'+payment_code+'";','protected $_isOffline = true;'])
	
		self.add_class(payment_class)

		payment_file = 'etc/payment.xml'

		payment_xml = Xmlnode('payment',attributes={'xmlns:xsi':"http://www.w3.org/2001/XMLSchema-instance","xsi:noNamespaceSchemaLocation":"urn:magento:module:Magento_Payment:etc/payment.xsd"},nodes=[
			Xmlnode('groups',nodes=[
				Xmlnode('group',attributes={'id':'offline'}, nodes=[
					Xmlnode('label',node_text='Offline Payment Methods')
				])
			]),
			Xmlnode('methods',nodes=[
				Xmlnode('method',attributes={'name':payment_code},nodes=[
					Xmlnode('allow_multiple_address',node_text='1'),
				])
			])
		]);

		self.add_xml(payment_file, payment_xml)

		config_file = 'etc/config.xml'

		config = Xmlnode('config',attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Store:etc/config.xsd"},nodes=[
			Xmlnode('default',nodes=[
				Xmlnode('payment',nodes=[
					Xmlnode(payment_code,nodes=[
						Xmlnode('active',node_text='1'),
						Xmlnode('model',node_text= payment_class.class_namespace),
						Xmlnode('order_status',node_text='pending'),
						Xmlnode('title',node_text=method_name),
						Xmlnode('allowspecific',node_text='0'),
						Xmlnode('group',node_text='Offline'),
					])
				])
			])
		]);

		self.add_xml(config_file, config)

		system_file = 'etc/adminhtml/system.xml'

		system = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:module:Magento_Config:etc/system_file.xsd"}, nodes=[
				Xmlnode('system',  nodes=[
					Xmlnode('section',attributes={'id':'payment','sortOrder':1000,'showInWebsite':1,'showInStore':1,'showInDefault':1,'translate':'label'},match_attributes={'id'},nodes=[
						Xmlnode('group', attributes={'id':payment_code,'sortOrder':10,'showInWebsite':1,'showInStore':1,'showInDefault':1,'translate':'label'},match_attributes={'id'},nodes=[
							Xmlnode('label',node_text=method_name),
							Xmlnode('field', attributes={'id':'active','type':'select','sortOrder':10,'showInWebsite':1,'showInStore':1,'showInDefault':1,'translate':'label'},match_attributes={'id'},nodes=[
								Xmlnode('label',node_text='New Order Status'),
								Xmlnode('source_model',node_text='Magento\\Config\\Model\\Config\\Source\\Yesno'),
							]),
							Xmlnode('field', attributes={'id':'title','type':'text','sortOrder':20,'showInWebsite':1,'showInStore':1,'showInDefault':1,'translate':'label'},match_attributes={'id'},nodes=[
								Xmlnode('label',node_text='Title'),
							]),
							Xmlnode('field', attributes={'id':'order_status','type':'select','sortOrder':30,'showInWebsite':1,'showInStore':1,'showInDefault':1,'translate':'label'},match_attributes={'id'},nodes=[
								Xmlnode('label',node_text='Enabled'),
								Xmlnode('source_model',node_text='Magento\\Sales\\Model\\Config\\Source\\Order\\Status\\NewStatus'),
							]),
							Xmlnode('field', attributes={'id':'allowspecific','type':'select','sortOrder':40,'showInWebsite':1,'showInStore':1,'showInDefault':1,'translate':'label'},match_attributes={'id'},nodes=[
								Xmlnode('label',node_text='Payment from Applicable Countries'),
								Xmlnode('source_model',node_text='Magento\\Payment\\Model\Config\\Source\\Allspecificcountries'),
							]),
							Xmlnode('field', attributes={'id':'specificcountry','type':'select','sortOrder':50,'showInWebsite':1,'showInStore':1,'showInDefault':1,'translate':'label'},match_attributes={'id'},nodes=[
								Xmlnode('label',node_text='Payment from Applicable Countries'),
								Xmlnode('source_model',node_text='Magento\\Directory\\Model\\Config\\Source\\Country'),
								Xmlnode('can_be_empty',node_text='1'),
							]),
							Xmlnode('field', attributes={'id':'sort_order','type':'text','sortOrder':60,'showInWebsite':1,'showInStore':1,'showInDefault':1,'translate':'label'},match_attributes={'id'},nodes=[
								Xmlnode('label',node_text='Sort Order'),
							]),
							Xmlnode('field', attributes={'id':'instructions','type':'textarea','sortOrder':70,'showInWebsite':1,'showInStore':1,'showInDefault':1,'translate':'label'},match_attributes={'id'},nodes=[
								Xmlnode('label',node_text='Instructions'),
							]),
						])	
					])
				])
		])

		self.add_xml(system_file,system)

		layout_file = 'view/frontend/layout/checkout_index_index.xml'

		layout_payment = Xmlnode('item',attributes={'name':'offline-payments','xsi:type':'array'},nodes=[
			Xmlnode('item',attributes={'name':'component','xsi:type':'string'},node_text='Magento_OfflinePayments/js/view/payment/offline-payments'),
			Xmlnode('item',attributes={'name':'methods','xsi:type':'array'},nodes=[
				Xmlnode('item',attributes={'name':payment_code,'xsi:type':'array'},nodes=[
					Xmlnode('item',attributes={'name':'isBillingAddressRequired','xsi:type':'boolean'},node_text='true')
				])
			])
		])

		layout_item = Xmlnode('item',attributes={'name':'components','xsi:type':'array'},nodes=[
			Xmlnode('item',attributes={'name':'checkout','xsi:type':'array'},nodes=[
				Xmlnode('item',attributes={'name':'children','xsi:type':'array'},nodes=[
					Xmlnode('item',attributes={'name':'steps','xsi:type':'array'},nodes=[
						Xmlnode('item',attributes={'name':'children','xsi:type':'array'},nodes=[
							Xmlnode('item',attributes={'name':'billing-step','xsi:type':'array'},nodes=[
								Xmlnode('item',attributes={'name':'children','xsi:type':'array'},nodes=[
									Xmlnode('item',attributes={'name':'payment','xsi:type':'array'},nodes=[
										Xmlnode('item',attributes={'name':'children','xsi:type':'array'},nodes=[
											Xmlnode('item',attributes={'name':'renders','xsi:type':'array'},nodes=[
												Xmlnode('item',attributes={'name':'children','xsi:type':'array'},nodes=[layout_payment])
											])
										])
									])
								])
							])
						])
					])
				])
			])
		])

		layout_base = Xmlnode('pagepage', attributes={'xmlns:xsi':"http://www.w3.org/2001/XMLSchema-instance",'layout':'1column', 'xsi:noNamespaceSchemaLocation':'urn:magento:framework:View/Layout/etc/page_configuration.xsd'}, nodes=[
			Xmlnode('body',nodes=[
				Xmlnode('referenceBlock',attributes={'name':'checkout.root'},nodes=[
					Xmlnode('arguments',nodes=[
						Xmlnode('argument',attributes={'name':'jsLayout','xsi:type':'array'},nodes=[layout_item])
					])
				])
			])
		])


		self.add_xml(layout_file,layout_base)

		self.add_static_file('view/frontend/web/template/payment', StaticFile(payment_code + '.html', template_file='payment/payment.tmpl',context_data={'module_name':self.module_name,'payment_code':payment_code}))
		self.add_static_file('view/frontend/web/js/view/payment', StaticFile(payment_code + '.js', template_file='payment/payment-js.tmpl',context_data={'module_name':self.module_name,'payment_code':payment_code}))
		self.add_static_file('view/frontend/web/js/view/payment/method-renderer', StaticFile(payment_code + '-method.js', template_file='payment/payment-method-js.tmpl',context_data={'module_name':self.module_name,'payment_code':payment_code}))

	@classmethod
	def params(cls):
		return [
			SnippetParam(
				name='method_name', 
				required=True, 
				description='Payment Method name. Example: Invoice, Credits',
				regex_validator= r'^[a-zA-Z]{1}\w+$',
				error_message='Only alphanumeric and underscore characters are allowed, and need to start with a alphabetic character.'),
		]	