import unittest
import os
import shutil
from context import mage2gen


class TestFullModuleCreation(unittest.TestCase):
	def test_full_module(self):
		module = mage2gen.Module(
			package='ExampleModule',
			name='ModuleName',
			description='Test module with all features Mage2Gen has to offer'
		)

		self.add_all_snippet_elements(module)

		# @TODO: Test all output against required output

		if os.path.isdir('./tmp/app/code/ExampleModule'):
			shutil.rmtree('./tmp/app/code/ExampleModule')

		if not os.path.isdir('./tmp/app/code'):
			os.makedirs('./tmp/app/code')

		module.generate_module(root_location='./tmp/app/code/')

	def add_all_snippet_elements(self, module) -> None:
		for (api_method, _) in mage2gen.snippets.ApiSnippet.API_METHOD_CHOISES:
			mage2gen.snippets.ApiSnippet(module).add(api_name='Example', api_method=api_method)
		mage2gen.snippets.BlockSnippet(module).add(classname='SampleBlock', methodname='printNotice')
		mage2gen.snippets.CategoryAttributeSnippet(module).add(attribute_label='Sample Category Attribute')
		mage2gen.snippets.CacheSnippet(module).add(name='SampleCache', description='Sample cache description')
		mage2gen.snippets.CompanyAttributeSnippet(module).add(attribute_label='Sample Attribute')
		mage2gen.snippets.ComponentSnippet(module).add(component_name='SampleComponent', style_type='scss')
		mage2gen.snippets.ConfigurationTypeSnippet(module).add(config_name='SampleConfig', node_name='sample', field_name='sample')
		mage2gen.snippets.ConsoleSnippet(module).add(action_name='SampleAction', short_description='Sample description')
		mage2gen.snippets.ControllerSnippet(module).add()
		mage2gen.snippets.CronjobSnippet(module).add(cronjob_class='SampleCronjob')
		mage2gen.snippets.CrongroupSnippet(module).add()
		mage2gen.snippets.CustomerAttributeSnippet(module).add(attribute_label='Sample Attribute')
		mage2gen.snippets.CustomerSectionDataSnippet(module).add(section_class='SampleSection')
		mage2gen.snippets.EavEntitySnippet(module).add(entity_name='SampleEntity')
		mage2gen.snippets.EavEntityAttributeSnippet(module).add(entity_model_class='SampleEntity', attribute_label='Sample Eav Attribute')
		mage2gen.snippets.GraphQlEndpointSnippet(module).add(base_type='Query', identifier='sample')
		mage2gen.snippets.GraphQlRouteLocatorSnippet(module).add(pagetype='SamplePageType', style_type='scss')
		mage2gen.snippets.HelperSnippet(module).add(helper_name='SampleHelper', add_enabled_function=True)
		mage2gen.snippets.LanguageSnippet(module).add()
		mage2gen.snippets.ModelSnippet(module).add(model_name='SampleModel', field_name='sample')
		mage2gen.snippets.ObserverSnippet(module).add(event='sample_event')
		mage2gen.snippets.PageBuilderContentTypeSnippet(module).add(content_type_name='SampleContentType', field_name='sample')
		mage2gen.snippets.PaymentSnippet(module).add(method_name='SamplePaymentMethod')
		mage2gen.snippets.PluginSnippet(module).add(classname='SampleClass', methodname='sampleMethod')
		mage2gen.snippets.PreferenceSnippet(module).add(classname='SampleClass')
		mage2gen.snippets.ProductAttributeSnippet(module).add(attribute_label='Sample Attribute')
		mage2gen.snippets.ProductTypeSnippet(module).add(product_type_code='SampleType', product_type_label='Sample Type')
		mage2gen.snippets.RouterSnippet(module).add()
		mage2gen.snippets.SalesAttributeSnippet(module).add(attribute_label='Sample Attribute')
		mage2gen.snippets.ShippingSnippet(module).add(method_name='SampleShippingMethod')
		mage2gen.snippets.SystemSnippet(module).add(tab='SampleTab', section='SampleSection', group='SampleGroup', field='SampleField')
		mage2gen.snippets.ViewModelSnippet(module).add(classname='SampleViewModel', methodname='sampleMethod', layout_handle='default', reference_name='content')
		mage2gen.snippets.WidgetSnippet(module).add(name='SampleWidget', field='sample')
		mage2gen.snippets.UnitTestSnippet(module).add(test_suite='SampleTestSuite', test_name='sampleTest')

	def tearDown(self):
		if os.path.isdir('./tmp'):
			shutil.rmtree('./tmp')
