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

	def test_add(self):
		php_class1 = mage2gen.Phpclass('\\Test\\Class1')
		php_class1.add_method(mage2gen.Phpmethod('getTest'))
		php_class2 = mage2gen.Phpclass('\\Test\\Class1')
		php_class2.add_method(mage2gen.Phpmethod('getTest2'))

		merged_class = php_class1 + php_class2

		self.assertEqual(len(merged_class.methods), 2)
		
