
.. image:: https://travis-ci.org/krukas/Mage2Gen.svg?branch=master
    :target: https://travis-ci.org/krukas/Mage2Gen
    
Mage2Gen
========

Mage2Gen is a python library for generating Magento 2 modules. It is
build to be extandeble with snippets for creating more complex Magento 2
modules based on simple input.

Installation
============
To install the Python library and the command line utility, run:

    pip install mage2gen

Example usage
=============

.. code:: python

    from mage2gen import Module

    # Create a module (Module1) for the package (Mage2gen)
    module = Module('Mage2gen', 'Module1')

    # Generate module files to folder (to_folder)
    module.generate_module('to_folder')

Snippets
========

Mage2Gen has core classes for creating and merging PHP classes, XML
files and static files. For generating a module you dont want to define
your PHP class or XML file for basic module concepts like observers,
plugins or controllers. This is where snippets comes in, witch add these
concepts based on simple input. The currently supported snippets are
listed below. If you like to add a snippet to Mage2Gen, simply fork this
project add you snippet or other improvements and create a pull request.

Controller
~~~~~~~~~~

Creates a controller with block, layout.xml and template. Can create a
controller for frontend and adminhtml.

Params:
-------
- **(str) frontname:** frontame route for module 
- **(str) section:** subfolder in module/Controller 
- **(str) action:** action class 
- **(bool) adminhtml [False]:** if controller is used for adminhtml

Example:
--------
.. code:: python

    from mage2gen.snippets import ControllerSnippet

    controller_snippet = ControllerSnippet(module)
    controller_snippet.add(frontname='mage2gen', section='order', action='json')

Plugin
~~~~~~

Creates a plugin for a public method, link to Magento 2 `docs`_

Params:
-------
- **(str) classname:** full class namespace of class withmethod 
- **(str) methodname:** method name of class 
- **(str) plugintype:** type fo plugin (before, after or around) 
- **(bool) sortorder [10]:** the order the plugin is executed in relation withother plugins. 
- **(bool) disabled [False]:** disable a plugin

Example:
--------
.. code:: python

    from mage2gen.snippets import PluginSnippet

    plugin_snippet = PluginSnippet(module)
    plugin_snippet.add('Magento\Catalog\Model\Product', 'getName')

Observer
~~~~~~~~

Create an observer for an event

Params:
-------
- **(str) event:** event name 
- **(int) scope [ObserverSnippet.SCOPE\_ALL]:** handle observer for all (SCOPE\_ALL), frontend (SCOPE\_FRONTEND) or backend (SCOPE\_ADMINHTML)

Example:
--------
.. code:: python

    from mage2gen.snippets import ObserverSnippet

    observer_snippet = ObserverSnippet(module)
    observer_snippet.add('catalog_product_save_after')

Create a Snippet
================

You can create you own snippets. If you like to add a snippet to
Mage2Gen, simply fork this project add you snippet or other improvements
and create a pull request.

Base snippet
~~~~~~~~~~~~

.. code:: python

    from mage2gen import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet

    class CustomSnippet(Snippet):
        def add(self, **params):
            # create and add PHP classes, XML and static files to the module
            
            # Get module name (<package>_<module>)
            self.module_name
            
            # Add PHP class to module (You can add the same class with different 
            # methods and attributes multiple times, Mage2Gen will merge them to 
            # one class with all the methods and attributes).
            self.add_class(PhpClassObject)
            
            # Add xml to module (Same as with the PHP class, you can add multiple
            # XML nodes for the same file !importend root node must be the same.
            # A XML node will be merge when the node name and the XML attributes 
            # name or id  are the same. When creating node you can say witch attributes
            # make the node unique, default is name and id).
            self.add_xml('full/path/to/xml/with/file/name', XmlNodeObject)
            
            # Add static file
            self.add_static_file('path/to/file/location', StaticFileObject)

Adding a PHP class
~~~~~~~~~~~~~~~~~~

TODO

Adding XML file
~~~~~~~~~~~~~~~

TODO

Adding Static file
~~~~~~~~~~~~~~~~~~

TODO

TODO
====

-  Increase test coverage.
-  [Nice to have] CLI interface for creating modules.
-  Adding more snippets:
    -  system.xml (Worked on by Derrick Heesbeen)
    -  Model attributes
    -  Custom models with adminhtml grid
    -  Adding fields to checkout process
    -  Shipping methods
    -  Payment methods
    
Example implementation:
~~~~~~

Mage2gen Online Magento Module Creator `mage2gen`_    

.. _docs: http://devdocs.magento.com/guides/v2.0/extension-dev-guide/plugins.html
.. _mage2gen: http://mage2gen.com
