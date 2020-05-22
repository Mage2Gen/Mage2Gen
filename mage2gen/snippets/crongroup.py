# Copyright © Experius All rights reserved.
# See COPYING.txt for license details.

from .. import Module, Phpclass, Phpmethod, Xmlnode, StaticFile, Snippet, SnippetParam, Readme
from ..utils import upperfirst


class CrongroupSnippet(Snippet):
    description = """With this snippet you can create a separate cron group. It will generate just a cron_groups.xml 
    file which is automatically loaded by Magento."""

    def add(self, cronjob_group='default', schedule_generate_every='15', schedule_ahead_for='20',
            schedule_lifetime='15', history_cleanup_every='10', history_success_lifetime='15',
            history_failure_lifetime='4320', use_separate_process='1', extra_params=None):
        crongroup_xml = Xmlnode('config', attributes={'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                                                      'xsi:noNamespaceSchemaLocation': "urn:magento:module:Magento_Cron:etc/cron_groups.xsd"},
                                nodes=[
                                    Xmlnode('group', attributes={'id': cronjob_group}, nodes=[
                                        Xmlnode('schedule_generate_every', node_text=schedule_generate_every),
                                        Xmlnode('schedule_ahead_for', node_text=schedule_ahead_for),
                                        Xmlnode('schedule_lifetime', node_text=schedule_lifetime),
                                        Xmlnode('history_cleanup_every', node_text=history_cleanup_every),
                                        Xmlnode('history_success_lifetime', node_text=history_success_lifetime),
                                        Xmlnode('history_failure_lifetime', node_text=history_failure_lifetime),
                                        Xmlnode('use_separate_process', node_text=use_separate_process),
                                    ])
                                ]);

        self.add_xml('etc/cron_groups.xml', crongroup_xml)

        self.add_static_file(
            '.',
            Readme(
                specifications=" - Crongroup\n\t- {}".format(cronjob_group),
            )
        )

    @classmethod
    def params(cls):
        return [
            SnippetParam(
                name='cronjob_group',
                required=True,
                default='default',
                description='Cronjob Group',
                regex_validator=r'^[a-z]{1}[a-z]+$',
                error_message='Only alphanumeric are allowed, and need to start with a alphabetic character.'),
            SnippetParam(
                name='schedule_generate_every',
                required=True,
                default='15',
                description='Schedule generate every',
                regex_validator=r'^\d+$',
                error_message='Only numeric value'),
            SnippetParam(
                name='schedule_ahead_for',
                required=True,
                default='20',
                description='Schedule ahead for',
                regex_validator=r'^\d+$',
                error_message='Only numeric value'),
            SnippetParam(
                name='schedule_lifetime',
                required=True,
                default='15',
                description='Schedule lifetime',
                regex_validator=r'^\d+$',
                error_message='Only numeric value'),
            SnippetParam(
                name='history_cleanup_every',
                required=True,
                default='10',
                description='History cleanup every',
                regex_validator=r'^\d+$',
                error_message='Only numeric value'),
            SnippetParam(
                name='history_success_lifetime',
                required=True,
                default='60',
                description='History success lifetime',
                regex_validator=r'^\d+$',
                error_message='Only numeric value'),
            SnippetParam(
                name='history_failure_lifetime',
                required=True,
                default='4320',
                description='History failure lifetime',
                regex_validator=r'^\d+$',
                error_message='Only numeric value'),
            SnippetParam(
                name='use_separate_process',
                required=True,
                default='1',
                description='Use separate process',
                regex_validator=r'^\d+$',
                error_message='Only numeric value'),

        ]
