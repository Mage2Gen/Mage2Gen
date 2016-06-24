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
import json
from collections import defaultdict, OrderedDict
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
from xml.dom import minidom

from mage2gen.utils import upperfirst

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')

###############################################################################
# PHP Class
###############################################################################
class Phpclass:

	template_file = os.path.join(TEMPLATE_DIR,'class.tmpl')

	def __init__(self, class_namespace, extends=None, implements=None, attributes=None, dependencies=None):
		self.class_namespace = self.upper_class_namespace(class_namespace)
		self.methods = set()
		self.extends = extends
		self.implements = implements if implements else []
		self.attributes = attributes if attributes else []
		self.dependencies = dependencies if dependencies else []

	def __eq__(self, other):
		return self.class_namespace == other.class_namespace

	def __add__(self, other):
		self.attributes = set(list(self.attributes) + list(other.attributes)) 
		self.methods = set(list(self.methods) + list(other.methods))
		return self

	@property
	def class_name(self):
		return self.class_namespace.split('\\')[-1]

	@property
	def namespace(self):
		return '\\'.join(self.class_namespace.split('\\')[:-1])

	def upper_class_namespace(self, class_namespace):
		return '\\'.join(upperfirst(n) for n in class_namespace.strip('\\').split('\\'))
	
	def add_method(self, method):
		self.methods = set(list(self.methods) + list([method]))

	def context_data(self):
		methods = '\n\n'.join(m.generate() for m in self.methods)
		if methods:
			methods = '\n' + methods

		attributes = '\n\t'.join(self.attributes)
		if attributes:
			attributes = '\n\t' + attributes

		dependencies = ';\n'.join("use %s" %(dependency) for dependency in self.dependencies)
		if dependencies:
			dependencies = '\n' + dependencies + ';'	

		return {
			'namespace': self.namespace,
			'class_name': self.class_name,
			'methods': methods,
			'extends': ' extends {}'.format(self.extends) if self.extends else '',
			'implements': ' implements {}'.format(', '.join(self.implements)) if self.implements else '',
			'attributes': attributes,
			'dependencies': dependencies
		}

	def generate(self):
		with open(self.template_file, 'rb') as tmpl:
			template = tmpl.read().decode('utf-8')

		return template.format(
			**self.context_data()
		)

	def save(self, root_location):
		path = os.path.join(root_location, self.class_namespace.replace('\\', '/') + '.php')
		try:
			os.makedirs(os.path.dirname(path))
		except Exception:
			pass
		
		with open(path, 'w+', encoding='utf-8') as class_file:
			class_file.writelines(self.generate())

class Phpmethod:
	PUBLIC = 'public'
	PROTECTED = 'protected'
	PRIVATE = 'private'

	def __init__(self, name, **kwargs):
		self.name = name
		self.access = kwargs.get('access', self.PUBLIC)
		self.params = kwargs.get('params', [])
		self.body = kwargs.get('body', '')
		self.template_file = os.path.join(TEMPLATE_DIR, 'method.tmpl')

	def __eq__(self, other):
		return self.name == other.name

	def __hash__(self):
		return hash(self.name)

	def params_code(self):
		length = sum(len(s) for s in self.params)
		if length > 40:
			return '\n\t\t' + ',\n\t\t'.join(self.params) + '\n\t'
		else:
			return ', '.join(self.params)

	def body_code(self):
		return '\n\t\t'.join(s.strip('\t') for s in self.body.splitlines())

	def generate(self):
		with open(self.template_file, 'rb') as tmpl:
			template = tmpl.read().decode('utf-8')

		return template.format(
			method=self.name,
			access=self.access,
			params=self.params_code(),
			body=self.body_code()
		)

###############################################################################
# XML
###############################################################################
class Xmlnode:

	def __init__(self, node_name, attributes=None, nodes=None, node_text=None, match_attributes=None):
		
		if nodes : 
			nodes = [x for x in nodes if x]

		self.node_name = node_name
		self.node_text = node_text
		self.attributes = attributes if attributes else {}
		self.match_attributes = match_attributes if match_attributes else ['name', 'id']
		self.nodes = nodes if nodes else []

	def __str__(self):
		return self.node_name

	def __eq__(self, other):
		if self.node_name != other.node_name:
			return False
		for key in self.match_attributes:	
			if key in self.attributes and self.attributes[key] != other.attributes[key]:
					return False
		return True

	def output_tree(self, depth=0):
		output = ("  " * depth) + "<{} {}>\n".format(self.node_name, self.attributes)
		for node in self.nodes:
			output += node.output_tree(depth + 1)
		return output

	def add_nodes(self, nodes):
		for node in nodes:
			if node in self.nodes and node.nodes:
				index = self.nodes.index(node)
				self.nodes[index].add_nodes(node.nodes)
			elif node not in self.nodes:
				self.nodes.append(node)

	def generate(self, element=None):
		if element != None:
			el = SubElement(element, self.node_name)
		else:
			el = Element(self.node_name)
			el.set('xmlns:xsi',"http://www.w3.org/2001/XMLSchema-instance")

		if self.node_text:
			el.text = self.node_text

		for key, value in self.attributes.items():
			el.set(str(key), str(value))

		for node in self.nodes:
			node.generate(el)

		if element == None:
			output = tostring(el, 'utf-8')
			reparsed = minidom.parseString(output)
			return reparsed.toprettyxml(indent="\t")

	def save(self, xml_path):
		try:
			os.makedirs(os.path.dirname(xml_path))
		except Exception:
			pass
		
		with open(xml_path, 'w+', encoding='utf-8') as xml_file:
			xml_file.writelines(self.generate())


###############################################################################
# Template files
###############################################################################
class StaticFile:

	def __init__(self, file_name, body=None, template_file='staticfile.tmpl', context_data=None):
		self.file_name = file_name
		self.template_file = os.path.join(TEMPLATE_DIR, template_file)
		self._context_data = context_data if context_data else {}
		self._context_data['body'] = body if body else ''

	def context_data(self):
		return self._context_data

	def generate(self):
		with open(self.template_file, 'rb') as tmpl:
			template = tmpl.read().decode('utf-8')

		return template.format(
			**self.context_data()
		)

	def save(self, file_path):
		try:
			os.makedirs(os.path.dirname(file_path))
		except Exception:
			pass
		
		with open(file_path, 'w+', encoding='utf-8') as static_file:
			static_file.writelines(self.generate())


###############################################################################
# Module
###############################################################################
class Module:

	def __init__(self, package, name, description=''):
		self.package = upperfirst(package)
		self.name = upperfirst(name)
		self.description = description
		self._xmls = {}
		self._classes = {}
		self._static_files = {}

		# minimum requirements for Magento2 module
		etc_module = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:framework:Module/etc/module.xsd"}, nodes=[
			Xmlnode('module', attributes={'name': self.module_name, 'setup_version': '1.0.0'})
		])
		self.add_xml('etc/module.xml', etc_module)

		self.add_static_file('.', StaticFile('registration.php', template_file='registration.tmpl', context_data={'module_name':self.module_name}))
		self._composer = OrderedDict()
		self._composer['name'] = '{}/{}'.format(self.package.lower(), self.name.lower())
		self._composer['description'] = self.description
		self._composer['authors'] = [
				{
					'name': 'Mage2Gen',
					'email': 'mail@mage2gen'
				}
			]
		self._composer['minimum-stability'] = 'dev'
		self._composer['require'] = {}
		self._composer['autoload'] = {
		        'files': [
		            'registration.php'
		        ],
		        'psr-4': {
		            "{}\\{}\\".format(self.package, self.name): ""
		        }
		    }

	@property
	def module_name(self):
	    return '{}_{}'.format(self.package, self.name)

	@classmethod
	def load_module(cls, data):
		# convert data
		return cls('Experius', 'Test')

	def generate_module(self, root_location):
		if not os.path.exists(root_location):
			raise Exception('Location does not exists')

		location = os.path.join(root_location, self.package, self.name)

		try:
			os.makedirs(location)
		except Exception:
			pass

		# Add composer as static file
		self.add_static_file('', StaticFile('composer.json', body=json.dumps(self._composer, indent=4)))

		for class_name, phpclass in self._classes.items():
			phpclass.save(root_location)

		for xml_file, node in self._xmls.items():
			path = os.path.join(location, xml_file)
			node.save(path)

		for path, static_file in self._static_files.items():
			path = os.path.join(location, path)
			static_file.save(path)

	def add_class(self, phpclass):
		root_namespace = '{}\{}'.format(self.package, self.name)
		if root_namespace not in phpclass.class_namespace:
			phpclass.class_namespace = '{}\{}'.format(root_namespace, phpclass.class_namespace)

		current_class = self._classes.get(phpclass.class_namespace)
		if current_class:
			current_class += phpclass
		else:
			current_class = phpclass
		self._classes[current_class.class_namespace] = current_class

	def add_xml(self, xml_file, node):
		current_xml = self._xmls.get(xml_file)
		if current_xml:
			if current_xml != node:
				raise Exception('Cant merge XML nodes root node must be the same')
			current_xml.add_nodes(node.nodes)
		else:
			self._xmls[xml_file] = node

	def add_static_file(self, path, staticfile):
		full_name = os.path.join(path, staticfile.file_name)
		if full_name not in self._static_files:
			self._static_files[full_name] = staticfile
