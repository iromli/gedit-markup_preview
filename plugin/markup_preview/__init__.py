# markup_preview.py - HTML preview of various markups in Gedit
# using WebKit and the GitHub cascading stylesheet.
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

import gconf
import gedit
import gtk
import os
import webkit
from gettext import gettext as _

from parser import MarkupParser, MARKUP_CHOICES


# Source: http://fgnass.posterous.com/github-markdown-preview
HTML_TEMPLATE = """<html><head><style type="text/css">
    .github {
        margin-left:auto;
        margin-right:auto;
        padding:0.7em;
        border:1px solid #E9E9E9;
        background-color:#f8f8f8;font-size:13.34px;
        font-family:helvetica,arial,freesans,clean,sans-serif;
        width:920px;
    }
    .github h1, h2, h3, h4, h5, h6 {border:0;}
    .github h1 {
        font-size:170%%;
        border-top:4px solid #aaa;
        padding-top:.5em;
        margin-top:1.5em;
    }
    .github h1:first-child {margin-top:0;padding-top:.25em;border-top:none;}
    .github h2 {
        font-size:150%%;
        margin-top:1.5em;
        border-top:4px solid #e0e0e0;
        padding-top:.5em;
    }
    .github h3 {margin-top:1em;}
    .github p {margin:1em 0;line-height:1.5em;}
    .github ul {margin:1em 0 1em 2em;}
    .github ol {margin:1em 0 1em 2em;}
    .github ul li {margin-top:.5em;margin-bottom:.5em;}
    .github ul ul, ul ol, ol ol, ol ul {margin-top:0;margin-bottom:0;}
    .github blockquote {
        margin:1em 0;
        border-left:5px solid #ddd;
        padding-left:.6em;
        color:#555;
    }
    .github dt {font-weight:bold;margin-left:1em;}
    .github dd {margin-left:2em;margin-bottom:1em;}
    .github table {margin:1em 0;}
    .github table th {border-bottom:1px solid #bbb;padding:.2em 1em;}
    .github table td {border-bottom:1px solid #ddd;padding:.2em 1em;}
    .github pre {
        margin:1em 0;
        font-size:12px;
        background-color:#f8f8ff;
        border:1px solid #dedede;
        padding:.5em;
        line-height:1.5em;
        color:#444;
        overflow:auto;
    }
    .github pre code {
        padding:0;
        font-size:12px;
        background-color:#f8f8ff;
        border:none;
    }
    .github code {
        font-size:12px;
        background-color:#f8f8ff;
        color:#444;
        padding:0 .2em;
        border:1px solid #dedede;
    }
    .github a {color:#4183c4;text-decoration:none;}
    .github a:hover {text-decoration:underline;}
    .github a code,a:link code,a:visited code{color:#4183c4;}
    .github img {max-width:100%%;}
</style></head><body><div class="github">%s</div></body></html>"""

UI = """<ui>
    <menubar name="MenuBar">
        <menu name="ToolsMenu" action="Tools">
            <placeholder name="ToolsOps_2">
                <menuitem name="MarkupPreview" action="MarkupPreview"/>
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

    def deactivate(self, window):
        self.instances[window].deactivate()
        del self.instances[window]

    def update_ui(self, window):
        self.instances[window].update_ui()

    def is_configurable(self):
        return True

    def create_configure_dialog(self):
        dialog = gtk.Dialog("Markup Preview Configuration")
        dialog.set_resizable(False)
        dialog.vbox.set_border_width(10)
        dialog.vbox.set_spacing(10)

        def on_toggled(widget):
            markup_preview_config('live_preview', widget.get_active())

        checkbox = gtk.CheckButton("Enable live preview")
        dialog.vbox.pack_start(checkbox)
        checkbox.show()
        checkbox.set_active(markup_preview_config('live_preview'))
        checkbox.connect('toggled', on_toggled)

        def on_closed(widget):
            gtk.Widget.destroy(dialog)

        close_button = dialog.add_button(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
        close_button.grab_default()
        close_button.connect('clicked', on_closed)

        return dialog


class MarkupPreview:

    def __init__(self, plugin, window):
        self.window = window
        self.plugin = plugin
        self.activate()

    def update_ui(self):
        if markup_preview_config('live_preview') is True:
            self.parse_document()

    def activate(self):
        panel = self.window.get_bottom_panel()
        manager = self.window.get_ui_manager()

        image = gtk.Image()
        image.set_from_icon_name("gnome-mime-text-html", gtk.ICON_SIZE_MENU)

        web_view = webkit.WebView()

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_property("hscrollbar-policy", gtk.POLICY_AUTOMATIC)
        scrolled_window.set_property("vscrollbar-policy", gtk.POLICY_AUTOMATIC)
        scrolled_window.set_property("shadow-type", gtk.SHADOW_IN)
        scrolled_window.add(web_view)
        scrolled_window.show_all()

        panel.add_item(scrolled_window, _("Markup Preview"), image)

        action_group = gtk.ActionGroup("MarkupPreviewActions")
        action_group.add_actions([
            ("MarkupPreview", None, _("Markup Preview"), "<Alt><Shift>M",
                _("Preview the HTML version."), self.parse_document)
        ], self.window)

        ui_id = manager.add_ui_from_string(UI)

        window_data = {
            'scrolled_window': scrolled_window,
            'web_view': web_view,
            'action_group': action_group,
            'ui_id': ui_id
        }

        manager.insert_action_group(window_data["action_group"], -1)
        manager.ensure_update()
        self.window.set_data('MarkupPreviewData', window_data)

    def deactivate(self):
        window_data = self.window.get_data('MarkupPreviewData')
        manager = self.window.get_ui_manager()
        manager.remove_ui(window_data["ui_id"])
        manager.remove_action_group(window_data["action_group"])

        panel = self.window.get_bottom_panel()
        panel.remove_item(window_data['scrolled_window'])

        self.window.set_data('MarkupPreviewData', None)
        self.plugin = None
        self.window = None
        manager.ensure_update()

    def parse_document(self, *args):
        window_data = self.window.get_data('MarkupPreviewData')
        view = self.window.get_active_view()
        if not view:
            return

        doc = view.get_buffer()
        start = doc.get_start_iter()
        end = doc.get_end_iter()

        if doc.get_selection_bounds():
            start = doc.get_iter_at_mark(doc.get_insert())
            end = doc.get_iter_at_mark(doc.get_selection_bound())

        markup = None
        file_ext = os.path.splitext(doc.get_short_name_for_display())[-1]
        if not file_ext:
            markup = doc.get_language().get_id()
        else:
            choices = MARKUP_CHOICES.iteritems()
            for format, ext in choices:
                if file_ext in ext:
                    markup = format
                    break
        if markup is None:
            return

        text = doc.get_text(start, end)
        markup_parser = MarkupParser(markup, text)
        content = markup_parser.parse()

        html = HTML_TEMPLATE % (content,)
        window_data['web_view'].load_string(html, 'text/html', 'iso-8859-15',
            'about:blank')

        bottom = self.window.get_bottom_panel()
        bottom.activate_item(window_data['scrolled_window'])
        bottom.set_property('visible', True)


def markup_preview_config(name, value=None):
        base = lambda x: u'/apps/gedit-2/plugins/markup_preview/%s' % x
        client = gconf.client_get_default()

        if value is not None:
            client.set_bool(base(name), value)
        return client.get_bool(base(name))
