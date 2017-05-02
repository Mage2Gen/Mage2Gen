
.. image:: https://travis-ci.org/krukas/Mage2Gen.svg?branch=master
    :target: https://travis-ci.org/krukas/Mage2Gen
    
Mage2Gen
========
Mage2Gen is a python library for generating Magento 2 modules. It is
build to be extendable with snippets for creating more complex Magento 2
modules based on simple input.

Installation
============
To install the Python library and the command line utility, run:

    sudo pip3 install mage2gen

Interactive command line
========================
With the mage2gen command line tool you can interactively create and generate Magento 2 modules.
If you have installed mage2gen for your whole system you can start it by running *mage2gen*.
You will be asked to give the module a package name, name and description:

.. code:: bash

    bash> mage2gen
    Package name [Mage2gen]: Mage2gen
    Module name: Test
    Description: A Mage2Gen test module
    
    Type help or ? to list commands.
    (Mage2Gen) 

Help
~~~~
You can use *help* or *?* to show all available commands and *help <command>* to show command specific help descriptions: 

.. code:: bash

    (Mage2Gen) help
    
    Documented commands (type help <topic>):
    ========================================
    add  exit  generate  help  info  list  remove
    
    Undocumented commands:
    ======================
    EOF
    
    (Mage2Gen) help add
    Add a snippet to the module

List snippets
~~~~~~~~~~~~~
With the *list* command you get a list of all the available snippets you can add to your module:

.. code:: bash

    (Mage2Gen) list
    console cronjob controller system plugin shipping install language observer payment

Add snippet
~~~~~~~~~~~
To add a snippet you can use the *add <snippet name>* command, you can auto-complete a snippet name with TAB:

.. code:: bash
    
    (Mage2Gen) add console
    Action name*: test
    Short description*: Test log command

Show added snippets
~~~~~~~~~~~~~~~~~~~
When you have added multiple snippets and you want to see which snippets are added to the module you can use the *info* command to show an overview:

.. code:: bash

    (Mage2Gen) info
    
    Mage2gen/Test
    
    Consoles
    
    Index  Action name  Short description  
    --------------------------------------------------------------------------------
    0      test         Test log command   
    --------------------------------------------------------------------------------

Remove snippet
~~~~~~~~~~~~~~
When you want to remove an added snippet you can use the *remove <snippet name> <index>* command, to remove the snippet from the module:

.. code:: bash

    (Mage2Gen) remove console 0
    Removed Console snippet

Generate module
~~~~~~~~~~~~~~~
When you are ready with your module and added the snippets you want to use, you can generate the module with the *generate* command. If you are inside a Magento 2 project directory, it will select the default path for the module:

.. code:: bash

    (Mage2Gen) generate
    Generate path [/media/data/Downloads/magento2/app/code]*: 
    Path does not exist, do you want to create it? [y/N]: y
    Module (Mage2gen/Test) generated to: /media/data/Downloads/magento2/app/code

Example usage library
=====================

.. code:: python

    from mage2gen import Module

    # Create a module (Module1) for the package (Mage2gen)
    module = Module('Mage2gen', 'Module1')

    # Generate module files to folder (to_folder)
    module.generate_module('to_folder')

Snippets
========

Mage2Gen has core classes for creating and merging PHP classes, XML
files and static files. For generating a module you don't want to define
your PHP class or XML file for basic module concepts like observers,
plugins or controllers. This is where snippets come in, which add these
concepts based on simple input. The currently supported snippets are
listed below. If you would like to add a snippet to Mage2Gen, simply fork this
project. Add your snippet or other improvements and create a pull request afterwards.

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
- **(str) classname:** full class namespace of class with method 
- **(str) methodname:** method name of class 
- **(str) plugintype:** type for plugin (before, after or around) 
- **(bool) sortorder [10]:** the order the plugin is executed in respect to other plugins. 
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

You can create your own snippets. If you would like to add a snippet to
Mage2Gen, simply fork this project. Add you snippet or other improvements
and create a pull request afterwards. You can read this `blog`_ post for an how to guide on creating a snippet.

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
            
            # Add XML to module (Same as with the PHP class, you can add multiple
            # XML nodes for the same file !important root node must be the same.
            # An XML node will be merged when the node name and the XML attributes 
            # name or id  are the same. When creating a node you can define which
            # attributes make the node unique, default is name and id).
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
-  Adding more snippets:
    -  Model attributes
    -  Custom models with adminhtml grid
    -  Adding fields to checkout process
    
Example implementation:
~~~~~~~~~~~~~~~~~~~~~~~

- Interactive command line
- Mage2gen Online Magento 2 Module Creator `mage2gen`_    

.. _docs: http://devdocs.magento.com/guides/v2.0/extension-dev-guide/plugins.html
.. _mage2gen: http://mage2gen.com
.. _blog: http://martens.me/programming/how-to-make-a-mage2gen-snippet.html
