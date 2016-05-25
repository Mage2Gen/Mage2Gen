import unittest
from context import mage2gen

class TestPhp(unittest.TestCase):
	
	def test_not_eq(self):
		php_class1 = mage2gen.Phpclass('\\Test\\Class1')
		php_class2 = mage2gen.Phpclass('\\Test\\Class2')
		self.assertFalse(php_class1 == php_class2)
	
	def test_eq(self):
		php_class1 = mage2gen.Phpclass('\\Test\\Class1')
		php_class2 = mage2gen.Phpclass('\\Test\\Class1')
		self.assertTrue(php_class1 == php_class2)

	def test_merge_methodes(self):
		php_class1 = mage2gen.Phpclass('\\Test\\Class1')
		php_class1.add_method(mage2gen.Phpmethod('getTest'))
		php_class2 = mage2gen.Phpclass('\\Test\\Class1')
		php_class2.add_method(mage2gen.Phpmethod('getTest2'))

		merged_class = php_class1 + php_class2

		self.assertEqual(len(merged_class.methods), 2)
		
	def test_merge_attributes(self):
		php_class1 = mage2gen.Phpclass('\\Test\\Class1', attributes=['test'])
		php_class2 = mage2gen.Phpclass('\\Test\\Class1', attributes=['test2'])

		merged_class = php_class1 + php_class2

		self.assertEqual(len(merged_class.attributes), 2)

	def test_class_namespace(self):
		php_class = mage2gen.Phpclass('\\Test\\Class1')

		self.assertEqual(php_class.class_namespace, 'Test\\Class1')

	def test_class_name(self):
		php_class = mage2gen.Phpclass('Test\\Model\\Class')

		self.assertEqual(php_class.class_name, 'Class')

	def test_namespace(self):
		php_class = mage2gen.Phpclass('Test\\Model\\Class')

		self.assertEqual(php_class.namespace, 'Test\\Model')
