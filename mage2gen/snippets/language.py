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

class LanguageSnippet(Snippet):
	description = """
	Magento 2 uses csv files for translations per language. This snippet will generate 
	a translation csv file for selected language with one example translation.

	- **language:** Language for translation file.

	Snippet generation
	------------------
	When you generate a module for the language *English (United States)*, it will create 
	a csv translation file in *i18n/en_US.csv*
	"""

	LANGUAGE_CHOISES = [
		('af_ZA', 'Afrikaans (South Africa)'),
		('sq_AL', 'Albanian (Albania)'),
		('ar_DZ', 'Arabic (Algeria)'),
		('ar_EG', 'Arabic (Egypt)'),
		('ar_KW', 'Arabic (Kuwait)'),
		('ar_MA', 'Arabic (Morocco)'),
		('ar_SA', 'Arabic (Saudi Arabia)'),
		('az_Latn_AZ', 'Azerbaijani (Azerbaijan)'),
		('eu_ES', 'Basque (Spain)'),
		('be_BY', 'Belarusian (Belarus)'),
		('bn_BD', 'Bengali (Bangladesh)'),
		('bs_Latn_BA', 'Bosnian (Bosnia and Herzegovina)'),
		('bg_BG', 'Bulgarian (Bulgaria)'),
		('ca_ES', 'Catalan (Spain)'),
		('zh_Hans_CN', 'Chinese (China)'),
		('zh_Hant_HK', 'Chinese (Hong Kong SAR China)'),
		('zh_Hant_TW', 'Chinese (Taiwan)'),
		('hr_HR', 'Croatian (Croatia)'),
		('cs_CZ', 'Czech (Czech Republic)'),
		('da_DK', 'Danish (Denmark)'),
		('nl_NL', 'Dutch (Netherlands)'),
		('en_AU', 'English (Australia)'),
		('en_CA', 'English (Canada)'),
		('en_IE', 'English (Ireland)'),
		('en_NZ', 'English (New Zealand)'),
		('en_GB', 'English (United Kingdom)'),
		('en_US', 'English (United States)'),
		('et_EE', 'Estonian (Estonia)'),
		('fil_PH', 'Filipino (Philippines)'),
		('fi_FI', 'Finnish (Finland)'),
		('fr_CA', 'French (Canada)'),
		('fr_FR', 'French (France)'),
		('gl_ES', 'Galician (Spain)'),
		('ka_GE', 'Georgian (Georgia)'),
		('de_AT', 'German (Austria)'),
		('de_DE', 'German (Germany)'),
		('de_CH', 'German (Switzerland)'),
		('el_GR', 'Greek (Greece)'),
		('gu_IN', 'Gujarati (India)'),
		('he_IL', 'Hebrew (Israel)'),
		('hi_IN', 'Hindi (India)'),
		('hu_HU', 'Hungarian (Hungary)'),
		('is_IS', 'Icelandic (Iceland)'),
		('id_ID', 'Indonesian (Indonesia)'),
		('it_IT', 'Italian (Italy)'),
		('it_CH', 'Italian (Switzerland)'),
		('ja_JP', 'Japanese (Japan)'),
		('km_KH', 'Khmer (Cambodia)'),
		('ko_KR', 'Korean (South Korea)'),
		('lo_LA', 'Lao (Laos)'),
		('lv_LV', 'Latvian (Latvia)'),
		('lt_LT', 'Lithuanian (Lithuania)'),
		('mk_MK', 'Macedonian (Macedonia)'),
		('ms_Latn_MY', 'Malay (Malaysia)'),
		('mn_Cyrl_MN', 'Mongolian (Mongolia)'),
		('nb_NO', 'Norwegian Bokmål (Norway)'),
		('nn_NO', 'Norwegian Nynorsk (Norway)'),
		('fa_IR', 'Persian (Iran)'),
		('pl_PL', 'Polish (Poland)'),
		('pt_BR', 'Portuguese (Brazil)'),
		('pt_PT', 'Portuguese (Portugal)'),
		('ro_RO', 'Romanian (Romania)'),
		('ru_RU', 'Russian (Russia)'),
		('sr_Cyrl_RS', 'Serbian (Serbia)'),
		('sk_SK', 'Slovak (Slovakia)'),
		('sl_SI', 'Slovenian (Slovenia)'),
		('es_AR', 'Spanish (Argentina)'),
		('es_CL', 'Spanish (Chile)'),
		('es_CO', 'Spanish (Colombia)'),
		('es_CR', 'Spanish (Costa Rica)'),
		('es_MX', 'Spanish (Mexico)'),
		('es_PA', 'Spanish (Panama)'),
		('es_PE', 'Spanish (Peru)'),
		('es_ES', 'Spanish (Spain)'),
		('es_VE', 'Spanish (Venezuela)'),
		('sw_KE', 'Swahili (Kenya)'),
		('sv_SE', 'Swedish (Sweden)'),
		('th_TH', 'Thai (Thailand)'),
		('tr_TR', 'Turkish (Turkey)'),
		('uk_UA', 'Ukrainian (Ukraine)'),
		('vi_VN', 'Vietnamese (Vietnam)'),
		('cy_GB', 'Welsh (United Kingdom)'),
	]

	def add(self, language='en_US'):
		self.add_static_file('i18n', StaticFile(language+'.csv','"string","stringtranslated"'))

	@classmethod
	def params(cls):
		return [
			SnippetParam(name='language', choises=cls.LANGUAGE_CHOISES, default='en_US')
		]