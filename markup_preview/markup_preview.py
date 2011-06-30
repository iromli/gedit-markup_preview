# markup_preview.py - HTML preview of various markups in Gedit using WebKit and the
# GitHub cascading stylesheet.
#
# Copyright (C) 2005 - Michele Campeotto
# Copyright (C) 2010 - Mihail Szabolcs
# Copyright (C) 2011 - Isman Firmansyah
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import gedit
import os
import gtk
import webkit
import markdown
import textile
from docutils import core
from gettext import gettext as _


# Source: http://fgnass.posterous.com/github-markdown-preview
HTML_TEMPLATE = """<html><head><style type="text/css">
 .github {margin-left:auto;margin-right:auto;padding:0.7em;border:1px solid #E9E9E9;background-color:#f8f8f8;font-size:13.34px;font-family:helvetica,arial,freesans,clean,sans-serif;width:920px;}
 .github h1,h2,h3,h4,h5,h6{border:0;}
 .github h1{font-size:170%%;border-top:4px solid #aaa;padding-top:.5em;margin-top:1.5em;}
 .github h1:first-child{margin-top:0;padding-top:.25em;border-top:none;}
 .github h2{font-size:150%%;margin-top:1.5em;border-top:4px solid #e0e0e0;padding-top:.5em;}
 .github h3{margin-top:1em;}
 .github p{margin:1em 0;line-height:1.5em;}
 .github ul{margin:1em 0 1em 2em;}
 .github ol{margin:1em 0 1em 2em;}
 .github ul li{margin-top:.5em;margin-bottom:.5em;}
 .github ul ul,ul ol,ol ol,ol ul,{margin-top:0;margin-bottom:0;}
 .github blockquote{margin:1em 0;border-left:5px solid #ddd;padding-left:.6em;color:#555;}
 .github dt{font-weight:bold;margin-left:1em;}
 .github dd{margin-left:2em;margin-bottom:1em;}
 .github table{margin:1em 0;}
 .github table th{border-bottom:1px solid #bbb;padding:.2em 1em;}
 .github table td{border-bottom:1px solid #ddd;padding:.2em 1em;}
 .github pre{margin:1em 0;font-size:12px;background-color:#f8f8ff;border:1px solid #dedede;padding:.5em;line-height:1.5em;color:#444;overflow:auto;}
 .github pre code{padding:0;font-size:12px;background-color:#f8f8ff;border:none;}
 .github code{font-size:12px;background-color:#f8f8ff;color:#444;padding:0 .2em;border:1px solid #dedede;}
 .github a{color:#4183c4;text-decoration:none;}
 .github a:hover{text-decoration:underline;}
 .github a code,a:link code,a:visited code{color:#4183c4;}
 .github img{max-width:100%%;}
</style></head><body><div class="github">%s</div></body></html>"""

UI = """
<ui>
  <menubar name="MenuBar">
    <menu name="ToolsMenu" action="Tools">
      <placeholder name="ToolsOps_2">
        <menuitem name="MP" action="MP"/>
      </placeholder>
    </menu>
  </menubar>
</ui>"""


class MarkupPreviewPlugin(gedit.Plugin):

    def __init__(self):
        gedit.Plugin.__init__(self)
        self.instances = {}

    def activate(self, window):
        self.instances[window] = MarkupPreview(self, window)
        self.instances[window].activate()

    def deactivate(self, window):
        self.instances[window].deactivate()
        del self.instances[window]


class MarkupPreview:

    def __init__(self, plugin, window):
        self.window = window
        self.plugin = plugin
        self.markup = None
        self.MARKUP_CHOICES = {
            'markdown': ['.markdown', '.md', '.mdown', '.mkd', '.mkdn'],
            'textile': ['.textile'],
            'rest': ['.rest', '.rst']
        }

    def activate(self):
        panel = self.window.get_bottom_panel()
        manager = self.window.get_ui_manager()

        image = gtk.Image()
        image.set_from_icon_name("gnome-mime-text-html", gtk.ICON_SIZE_MENU)

        self._web_view = webkit.WebView()
        self._scrolled_window = gtk.ScrolledWindow()
        self._scrolled_window.set_property("hscrollbar-policy",
            gtk.POLICY_AUTOMATIC)
        self._scrolled_window.set_property("vscrollbar-policy",
            gtk.POLICY_AUTOMATIC)
        self._scrolled_window.set_property("shadow-type", gtk.SHADOW_IN)
        self._scrolled_window.add(self._web_view)
        self._scrolled_window.show_all()

        panel.add_item(self._scrolled_window, "Markup Preview", image)

        self._ui_id = manager.add_ui_from_string(UI)

        self._action_group = gtk.ActionGroup("MPActions")
        self._action_group.add_actions([
            ("MP", None, _("Markup Preview"), "<Alt><Shift>M",
                _("Updates the markup HTML preview."), self.update_preview)
        ])

        manager.insert_action_group(self._action_group, -1)
        manager.ensure_update()

    def deactivate(self):
        manager = self.window.get_ui_manager()
        manager.remove_ui(self._ui_id)
        manager.remove_action_group(self._action_group)

        panel = self.window.get_bottom_panel()
        panel.remove_item(self._scrolled_window)

        manager.ensure_update()

        self.plugin = None
        self.window = None

    def connect_document(self, doc):
        try:
            handler_id = doc.connect("saved", self.on_document_saved)
            doc.set_data("MPData", handler_id)
        except AttributeError:
            pass

    def on_document_saved(self, doc, *args):
        if not self.markup:
            return

    def update_preview(self, *args):
        view = self.window.get_active_view()
        if not view:
            return

        doc = view.get_buffer()
        start = doc.get_start_iter()
        end = doc.get_end_iter()

        if doc.get_selection_bounds():
            start = doc.get_iter_at_mark(doc.get_insert())
            end = doc.get_iter_at_mark(doc.get_selection_bound())

        text = doc.get_text(start, end)
        content = '<p>Cannot render this file -- unsupported markup or file extension!</p>'

        choices = self.MARKUP_CHOICES.iteritems()
        file_ext = os.path.splitext(doc.get_short_name_for_display())[-1]

        for format, ext in choices:
            if file_ext in ext:
                self.markup = format
                break

        if self.markup == 'markdown':
            content = markdown.markdown(text)
        elif self.markup == 'rest':
            extras = {'initial_header_level': '2'}
            content = core.publish_parts(text, writer_name='html',
                settings_overrides=extras)
            content = content.get('html_body')
        elif self.markup == 'textile':
            content = textile.textile(text)

        html = HTML_TEMPLATE % (content,)
        self._web_view.load_string(html,'text/html','iso-8859-15','about:blank')

        bottom = self.window.get_bottom_panel()
        bottom.activate_item(self._scrolled_window)
        bottom.set_property('visible',True)
