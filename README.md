# Mage2Gen

Mage2Gen is a python library for generating Magento 2 modules. It is build to be extandeble with snippets for adding more complex Magento 2 modules.

Current Supported snippets 
==========================

* **Controller action** with block, layout.xml and template for frontend and adminhtml

Example usage
============
```python
from mage2gen import Module
from mage2gen.snippets import ControllerSnippet, PluginSnippet, ObserverSnippet

module = Module('Mage2gen', 'Module1')

controller_snippet = ControllerSnippet(module)
controller_snippet.add(frontname='mage2gen', section='order', action='json')
controller_snippet.add(frontname='mage2gen', section='order', action='json', adminhtml=True)

plugin_snippet = PluginSnippet(module)
plugin_snippet.add('Magento\Catalog\Model\Product', 'getName')
plugin_snippet.add('Magento\Catalog\Model\Product', 'getName' sortorder=10, disabled=True, plugintype=PluginSnippet.TYPE_AROUND)

observer_snippet = ObserverSnippet(module)
observer_snippet.add('catalog_product_save_after')
observer_snippet.add('catalog_product_save_after', ObserverSnippet.SCOPE_FRONTEND)

module.generate_module('to_folder')
```

Example snippet
==============
TODO
