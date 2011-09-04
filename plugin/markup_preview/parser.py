# -*- coding: utf-8 -*-
import markdown
import textile
from docutils import core


MARKUP_CHOICES = {
    'markdown': ['.markdown', '.md', '.mdown', '.mkd', '.mkdn'],
    'textile': ['.textile'],
    'restructuredtext': ['.rest', '.rst']
}


class MarkupParser():

    def __init__(self, markup, text):
        self.markup = markup
        self.text = text

    def parse(self):
        if self.markup == 'markdown':
            content = markdown.markdown(self.text)
        elif self.markup == 'restructuredtext':
            extras = {'initial_header_level': '2'}
            content = core.publish_parts(self.text, writer_name='html',
                settings_overrides=extras)
            content = content.get('html_body')
        elif self.markup == 'textile':
            content = textile.textile(self.text)
        else:
            content = ''
        return content
