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
import os, locale
from mage2gen import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam

class ProductAttributeSnippet(Snippet):
    snippet_label = 'Product Attribute'

    FRONTEND_INPUT_TYPE = [
        ("text","Text Field"),
        ("textarea","Text Area"),
        ("date","Date"),
        ("boolean","Yes/No"),
        ("multiselect","Multiple Select"),
        ("select","Dropdown"),
        ("price","Price"),
        ("static","Static")
        #("media_image","Media Image"),
        #("weee","Fixed Product Tax"),
        #("swatch_visual","Visual Swatch"),
        #("swatch_text","Text Swatch")
    ]

    STATIC_FIELD_TYPES = [
        ("varchar","Varchar"),
        ("text","Text"),
        ("int","Int"),
        ("decimal","Decimal")
    ]

    FRONTEND_INPUT_VALUE_TYPE = {
        "text":"varchar",
        "textarea":"text",
        "date":"date",
        "boolean":"int",
        "multiselect":"varchar",
        "select":"int",
        "price":"decimal",
        #"media_image":"",
        #"weee":"",
        #"swatch_visual":"",
        #"swatch_text":""
    }

    SCOPE_CHOICES = [
        ("0","SCOPE_STORE"),
        ("1","SCOPE_GLOBAL"),
        ("2","SCOPE_WEBSITE")
    ]

    # APPLY_TO_CHOICES = [
    #     ("0","All Product Types"),
    #     ("simple","Simple Products"),
    #     ("grouped","Grouped Products"),
    #     ("bundle","Bundled Products"),
    #     ("configurable","Configurable Products")
    # ]

    description = """
        Install Magento 2 product attributes programmatically. 

        The attribute is automatically added to all the attribute sets.
    """
    
    def add(self,attribute_label,frontend_input='text',required=False,scope=1,options=None,extra_params=None):
        extra_params = extra_params if extra_params else {}
        attribute_code = attribute_label.lower().replace(' ','_');
        value_type = self.FRONTEND_INPUT_VALUE_TYPE.get(frontend_input,'int');
        user_defined = 'true'
        options = options.split(',') if options else []
        options_php_array = '"'+'","'.join(x.strip() for x in options) + '"'
        options_php_array_string = "array('values' => array("+options_php_array+"))"
        methodName = 'install' + attribute_label + 'ProductAttribute'

        templatePath = os.path.join(os.path.dirname(__file__), '../templates/attributes/productattribute.tmpl')

        with open(templatePath, 'rb') as tmpl:
            template = tmpl.read().decode('utf-8')

        methodBody = template.format(
            attribute_code=attribute_code,
            attribute_label=attribute_label,
            value_type=value_type,
            frontend_input=frontend_input,
            user_defined = user_defined,
            scope = scope,
            required = required,
            options = options_php_array_string,
            searchable = extra_params.get('searchable','false'),
            filterable = extra_params.get('filterable','false'),
            visible_on_front = extra_params.get('visible_on_front','false'),
            comparable = extra_params.get('comparable','false'),
            used_in_product_listing = extra_params.get('used_in_product_listing','false'),
            unique = extra_params.get('unique','false'),
            default = extra_params.get('default','0'),
            is_visible_in_advanced_search = extra_params.get('is_visible_in_advanced_search','0')
        )

        install_data = Phpclass('Setup\\InstallData',implements=['InstallDataInterface'],dependencies=['Magento\\Framework\\Setup\\InstallDataInterface','Magento\\Framework\\Setup\\ModuleContextInterface','Magento\\Framework\\Setup\\ModuleDataSetupInterface','Magento\\Eav\\Setup\\EavSetup','Magento\\Eav\\Setup\\EavSetupFactory'])
        install_data.attributes.append('private $eavSetupFactory;')
        install_data.add_method(Phpmethod(
            '__construct',
            params=[
                'EavSetupFactory $eavSetupFactory',
            ],
            body="$this->eavSetupFactory = $eavSetupFactory;"
        )) 
        install_data.add_method(Phpmethod('install',params=['ModuleDataSetupInterface $setup','ModuleContextInterface $context'],body="$eavSetup = $this->eavSetupFactory->create(['setup' => $setup]);"))
        install_data.add_method(Phpmethod('install',params=['ModuleDataSetupInterface $setup','ModuleContextInterface $context'],body=methodBody))
    
        self.add_class(install_data)
    
    @classmethod
    def params(cls):
         return [
             SnippetParam(
                name='attribute_label', 
                required=True, 
                description='Tab code. Example: catalog',
                regex_validator= r'^[a-zA-Z\d\-_\s]+$',
                error_message='Only alphanumeric'),
             SnippetParam(
                 name='frontend_input', 
                 choises=cls.FRONTEND_INPUT_TYPE,
                 required=True,  
                 default='text'),
             SnippetParam(
                name='options',
                depend= {'frontend_input': r'select|multiselect'}, 
                required=False, 
                description='Dropdown or Multiselect options comma seperated',
                error_message='Only alphanumeric'),
             SnippetParam(
                 name='required',
                 required=True,  
                 default=True,
                 yes_no=True),
             SnippetParam(
                 name='scope',
                 required=True,  
                 choises=cls.SCOPE_CHOICES, 
                 default='1'),
         ]

    @classmethod
    def extra_params(cls):
         return [
             SnippetParam(
                 name='searchable',
                 required=True,  
                 default=False,
                 yes_no=True),
             SnippetParam(
                 name='filterable',
                 required=True,  
                 default=False,
                 depend= {'frontend_input': r'select|multiselect|price'}, 
                 yes_no=True),
             SnippetParam(
                 name='visible_on_front',
                 required=True,  
                 default=False,
                 yes_no=True),
             SnippetParam(
                 name='comparable',
                 required=True,  
                 default=False,
                 yes_no=True),
             SnippetParam(
                 name='used_in_product_listing',
                 required=True,  
                 default=False,
                 yes_no=True),
             SnippetParam(
                 name='unique',
                 required=True,  
                 default=False,
                 yes_no=True),
         ]