Mage2Gen
========

Mage2Gen is a python library for generating Magento 2 modules. It is
build to be extandeble with snippets for creating more complex Magento 2
modules based on simple input.

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

    python from mage2gen import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet

    class CustomSnippet(Snippet): 
        def add(self, **params): # create and add PHP classes, XML and static files to the module

        # Get module name (<package>_<module

.. _docs: http://devdocs.magento.com/guides/v2.0/extension-dev-guide/plugins.html

