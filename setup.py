try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name = 'Mage2Gen',
	packages = ['mage2gen', 'mage2gen.snippets'],
	package_data={'mage2gen': ['templates/*.tmpl']},
	version = '0.2',
	description = 'Magento 2 module generator',
	author = 'Maikel Martens',
	author_email = 'maikel@martens.me',
	url = 'https://github.com/krukas/Mage2Gen',
	download_url = 'https://github.com/krukas/Mage2Gen/releases/tag/0.2',
	keywords = ['Magento', 'Magento2', 'module', 'generator'],
	classifiers = [],
	install_requires=[],
)