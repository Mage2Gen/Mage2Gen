# A Magento 2 module generator library
# Copyright (C) 2019 Mr. Lewis
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
import os
from .. import StaticFile, Snippet, SnippetParam

class ComponentSnippet(Snippet):

	description = """Create React Component"""

	STYLE_CSS = 'css'
	STYLE_SCSS = 'scss'

	STYLES_CHOISES = [
		(STYLE_CSS, 'css'),
		(STYLE_SCSS, 'sass'),
	]

	def add(self, component_name, style_type, extra_params=None):
		# Add Component File
		path = os.path.join('src', 'components', self._module.package, self._module.name)
		self.add_static_file(path, StaticFile(
				'index.js',
				body="""export {{ default }} from './{component_name}';""".format(
					component_name=component_name
				)
			)
		)
		componentFile = '{}.js'.format(component_name)
		self.add_static_file(path, StaticFile(
				componentFile,
				body="""
import React, {{ Component }} from 'react';
import PropTypes, {{ shape, string }} from 'prop-types';
import classify from 'src/classify';
import defaultClasses from './{component_name}.{style_type}';
import Placeholder from "./placeholder";

class {class_name} extends Component {{
	static propTypes = {{
		classes: shape({{
			scope: string,
			button: string
		}}),
		id: string
	}};

	render() {{
		const {{ id, classes }} = this.props;

		return (<div>Example</div>);
	}}
}}
				""".format(
					component_name=component_name,
					class_name=component_name,
					style_type=style_type
				)
			)
		)

		scssFile = '{}.{}'.format(component_name, style_type)
		self.add_static_file(path, StaticFile(
			scssFile,
			body="""
.test {

}
				"""
			)
	 	)

	@classmethod
	def params(cls):
		return [
			SnippetParam(name='component_name', required=True,
				description='Example: carousel',
				regex_validator=r'^[\w\\]+$',
				error_message='Only alphanumeric, underscore and backslash characters are allowed'),
			SnippetParam(name='style_type',
				choises=cls.STYLES_CHOISES,
				default=cls.STYLE_CSS),
		]