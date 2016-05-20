import os
from collections import defaultdict
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
from xml.dom import minidom

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')

def upperfirst(word):
	return word[0].upper() + word[1:]

###############################################################################
# PHP Class
###############################################################################
class Phpclass:

	def __init__(self, class_namespace, extends=None, attributes=None):
		self.class_namespace = self.upper_class_namespace(class_namespace)
		self.methods = set()
		self.template_file = os.path.join(TEMPLATE_DIR, 'class.tmpl')
		self.extends = extends
		self.attributes = attributes if attributes else []

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
		return '\\'.join(upperfirst(n) for n in class_namespace.split('\\'))
	
	def add_method(self, method):
		self.methods = set(list(self.methods) + list([method]))

	def generate(self):
		with open(self.template_file, 'r') as tmpl:
			template = tmpl.read()

		methods = '\n\n'.join(m.generate() for m in self.methods)
		if methods:
			methods = '\n' + methods

		attributes = '\n\t'.join(self.attributes)
		if attributes:
			attributes = '\n\t' + attributes

		return template.format(
			namespace=self.namespace,
			class_name=self.class_name,
			methods=methods,
			extends=' extends {}'.format(self.extends) if self.extends else '',
			attributes=attributes
		)

	def save(self, root_location):
		path = os.path.join(root_location, self.class_namespace.replace('\\', '/') + '.php')
		try:
			os.makedirs(os.path.dirname(path))
		except Exception:
			pass
		
		with open(path, 'w+') as class_file:
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
		with open(self.template_file, 'r') as tmpl:
			template = tmpl.read()

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

	def __init__(self, node_name, name=None, attributes=None, nodes=None):
		self.node_name = node_name
		self.name = name
		self.attributes = attributes if attributes else {}
		self.nodes = nodes if nodes else []

	def __str__(self):
		return self.node_name

	def __eq__(self, other):
		if self.node_name != other.node_name:
			return False
		if self.name != other.name:
			return False
		return True

	def output_tree(self, depth=0):
		output = ("  " * depth) + "<{} name='{}' {}>\n".format(self.node_name, self.name, self.attributes)
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

		if self.name:
			el.set('name', self.name)

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
		
		with open(xml_path, 'w+') as xml_file:
			xml_file.writelines(self.generate())


###############################################################################
# Template files
###############################################################################
class StaticFile:

	def __init__(self, file_name, body=None):
		self.file_name = file_name
		self.body = body if body else ''

	def generate(self):
		return self.body

	def save(self, file_path):
		try:
			os.makedirs(os.path.dirname(file_path))
		except Exception:
			pass
		
		with open(file_path, 'w+') as static_file:
			static_file.writelines(self.generate())


###############################################################################
# Module
###############################################################################
class Module:

	def __init__(self, package, name):
		self.package = upperfirst(package)
		self.name = upperfirst(name)
		self._xmls = {}
		self._classes = {}
		self._static_files = {}

		# minimum requirements for Magento2 module
		etc_module = Xmlnode('config', attributes={'xsi:noNamespaceSchemaLocation':"urn:magento:framework:Module/etc/module.xsd"}, nodes=[
			Xmlnode('module', self.module_name, attributes={'setup_version': '1.0.0'})
		])
		self.add_xml('etc/module.xml', etc_module)

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

		# Generate registration
		with open(os.path.join(TEMPLATE_DIR, 'registration.tmpl'), 'r') as tmpl:
			template = tmpl.read()

		with open(os.path.join(location, 'registration.php'), 'w+') as reg_file:
			reg_file.writelines(template.format(module_name=self.module_name))		

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