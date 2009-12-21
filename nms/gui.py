#-*- coding: utf-8 -*-
import gtk
from os import path
from gtk import glade
from copy import copy as ccopy
from pygtkhelpers.ui.objectlist import Column, ObjectList
from jinja2 import nodes as jnodes
from nms import ctx, get_copyright, VERSION, LICENSE, AUTHORS, ARTISTS
from nms.database import db, metadata, Recipient, recipients_table
from nms.utils.dialogs import new_recipient_dialog
from nms.utils.html import PangoHTMLRenderer, PangoPlainRenderer
from nms.utils.themes import find_themes
from nms.utils.gtkhelpers import BaseDialog, BaseWindow, TextBuffer, \
    scrolled



(SEND_NEWSLETTER, CANCEL_SEND_NEWSLETTER) = range(2)


class PreferencesDialog(BaseDialog):

    def __init__(self, parent):
        BaseDialog.__init__(self, 'preferences',
            parent, 'core.glade')
        ctx.logger.debug('initalizing preferences dialog')

        # init some data
        mapping = self.mail_cfg = {
            'smtp_host':            'text',
            'smtp_user':            'text',
            'smtp_password':        'text',
            'mail_encoding':        'text',
            'mail_default_from':    'text',
            'smtp_port':            'value',
            'smtp_use_tls':         'active',
            'smtp_raise_error':     'active',
            'debug':                'active',
            'log_timeformat':       'text',
        }
        cfg, w = ctx.settings, self.widgets
        # load values from the preferences module and visualize
        # them in the preferences dialog
        for widget, property in mapping.iteritems():
            w[widget].set_property(property, cfg[widget])
        ctx.logger.debug('loaded preferences from database')

        # the combo box to change the active project
        self._themes = ObjectList([
            Column('display_name', str, 'Name'),
            Column('author', str, 'Autor')
        ])
        self._themes.connect('item-activated', self.on_theme_choice_changed)
        self._themes.set_border_width(10)
        self.widgets.theme_vbox.pack_end(self._themes)
        # add all themes to the combo
        self._refresh_themes()

        # init the recipients ObjectList
        vbox = self.widgets.recipients_vbox
        self._recipients = ObjectList([
            Column('name', str, 'Name', editable=True),
            Column('mail', str, 'E-Mail', editable=True),
            Column('active', str, 'Mail senden', editable=True),
            Column('comment', str, 'Bemerkung', editable=True)
        ])
        self._recipients.connect('item-changed', self._on_recipient_edited)
        vbox.pack_start(self._recipients)
        self._update_recipients()
        self._recipients.show()
        ctx.logger.debug('inialized recipients preferences dialog-page')

    def on_add_recipient_button_clicked(self, sender, arg=None):
        ctx.logger.debug('add_recipient_button clicked')
        rdata = new_recipient_dialog(u'Neuer Empfänger',
            u'Trage hier die Daten für einen neuen Empfänger ein.')
        if rdata is not None:
            recipient = Recipient(*rdata)
            self._recipients.append(recipient)
            db.save(recipient)
            db.commit()

    def on_delete_recipient_button_clicked(self, sender, arg=None):
        ctx.logger.debug('delte_recipient_button clicked')
        obj = self._recipients.get_selected()
        if obj is not None:
            self._recipients.remove(obj)
            db.delete(obj)
            db.commit()

    def _update_recipients(self):
        rlist = set(self._recipients)
        rdb = set(db.query(Recipient).order_by(Recipient.name).all())
        rdiff = list(rdb - rlist)
        if rdiff:
            if len(rdiff) > 1:
                self._recipients.extend(rdiff)
            else:
                self._recipients.append(rdiff[0])

    def _on_recipient_edited(self, sender, object, attr, value):
        db.commit()
        ctx.logger.debug('recipient edited')

    @property
    def recipients(self):
        self._update_recipients()
        return self._recipients

    def _refresh_themes(self):
        self._themes.clear()
        a = None
        themes = list(find_themes())
        if not themes:
            self._themes.hide()
            self.widgets.no_themes_found.show()
        else:
            for theme in themes:
                self._themes.append(theme)
                if theme.name ==  ctx.theme_loader.current.name:
                    a = theme
            if a: self._themes.select(a)
            self.widgets.no_themes_found.hide()
            self._themes.show()
        ctx.logger.debug('themes refreshed and repacked')

    def on_theme_choice_changed(self, object, attr, value):
        # set the new theme in ctx.settings
        if obj is not None:
            ctx.settings['theme_choice'] = obj.name
            sender.emit_stop_by_name('selection-changed')
        ctx.logger.debug('theme choice changed to %s'
            % ctx.settings['theme_choice'])

    def on_theme_path_selection_changed(self, sender):
        new_dir = self.widgets.theme_chooser.get_current_folder()
        ctx.settings['theme_path'] = new_dir
        sender.emit_stop_by_name('current-folder-changed')
        self._refresh_themes()
        ctx.logger.debug('theme path changed to %s' % new_dir)

    def get_response_data(self):
        cfg, w = ctx.settings, self.widgets
        return dict((x, w[x].get_property(y)) for x, y in \
                    self.mail_cfg.iteritems())


class EditorWindow(BaseWindow):

    def __init__(self, parent):
        BaseWindow.__init__(self, 'editor', parent, 'core.glade')

        # bind widgets
        self.statusbar = self.widgets.statusbar
        self.set_statusbar_msg('initial_message', 'Newsletter Mail System gestartet')
        self.window.maximize()

        theme = ctx.theme_loader.current
        nodes = reversed(theme.token_tree.find_all(jnodes.Block))

        wrapper = self.widgets.text_wrapper
        self.text_views = []
        for node in nodes:
            expander = gtk.Expander(node.name)
            vbox = gtk.VBox()
            view = gtk.TextView()
            view.set_buffer(TextBuffer())
            buffer = view.get_buffer()
            for signal in ('copy', 'paste', 'cut'):
                view.connect(signal+'-clipboard',
                             getattr(self, 'on_%s' % signal))
            view.set_property('height-request', 250)
            view.set_property('can-focus', True)
            self.text_views.append(view)
            vbox.pack_start(scrolled(view, height=200))
            expander.add(vbox)
            wrapper.pack_start(expander, False, False, 5)
            sep = gtk.HSeparator()
            sep.set_property('height-request', 5)
            wrapper.pack_start(sep, False, False, 10)
        wrapper.show_all()

        for view in self.text_views:
            buf = view.get_buffer()
            #TEST
            buf.set_text('bold, italic, normal, \n\n\n\n And now some underlined text...'
                        '\n\nBut delted text is also possible....')
            ao = buf.get_iter_at_offset
            buf.toggle_wrap_text((ao(0), ao(4)), 'bold')
            buf.toggle_wrap_text((ao(6), ao(12)), 'italic')
            buf.toggle_wrap_text((ao(27), ao(55)), 'underline')
            buf.toggle_wrap_text((ao(60), ao(92)), 'strikethrough')
            renderer = PangoHTMLRenderer(buf)
            print renderer.get_tags()
            #print '---------------------------------------------------------\n\n'
            #print renderer.get_text()
            #print '---------------------------------------------------------\n\n'
            #print PangoPlainRenderer(buf).get_text()
        ctx.logger.debug('initalized editor window')

    def on_style_button_clicked(self, sender, type=None):
        type = type is None and sender.name.split('_', 1)[1] or type
        buf = self.get_active_buffer()
        if type in ('bold', 'italic', 'underline', 'strikethrough'):
            buf.toggle_wrap_text(None, type)
        else:
            self.set_statusbar_msg('error', u'„%s“ Formatierung zZ nicht unterstützt' % type)
        ctx.logger.debug('style button "%s" clicked' % type)

    @property
    def text(self):
        tb = self.textview.get_buffer()
        start, end = (tb.get_start_iter(), tb.get_end_iter())
        return tb.get_text(start, end)

    def set_statusbar_msg(self, desc, msg):
        ctx = self.statusbar.get_context_id(desc or '')
        id = self.statusbar.push(ctx, '  ' + msg + '...')
        return (id, ctx)

    def on_cut(self, sender, arg=None):
        """
        Copy the text of the activated (or of the text buffer) into the
        clipboard.
        """
        buf = self.get_active_buffer()
        if buf is not None:
            buf.cut_clipboard(sender, arg)

    def on_delete(self, sender, arg=None):
        """Delete the selected text."""
        self.modify_selection(lambda *a: '')

    def on_copy(self, sender, arg=None):
        """Copy selected text to clipboard."""
        buf = self.get_active_buffer()
        if buf is not None:
            buf.copy_clipboard(sender, arg)

    def on_paste(self, sender, arg=None):
        """Paste from the clipboard into the active (or text) buffer."""
        buf = self.get_active_buffer()
        if buf is not None:
            buf.paste_clipboard(sender, arg)

    def get_active_buffer(self, fallback=True):
        for view in self.text_views:
            if view.get_property('has-focus'):
                return view.get_buffer()
        if fallback:
            return self.text_views[0].get_buffer()

    def on_about(self, sender, arg=None):
        MainWindow.on_about(sender, arg)


class MainWindow(BaseWindow):

    def __init__(self):
        BaseWindow.__init__(self, 'main_window', filename='core.glade')

    def on_new_newsletter_button_clicked(self, sender, arg=None):
        editor = EditorWindow(self.window)
        editor.show()

    def on_preferences_button_clicked(self, sender, arg=None):
        preferences = PreferencesDialog(self.window)
        nc = preferences.run()
        if nc:
            ctx.settings.update(**nc)

    def on_quit_button_clicked(self, sender, arg=None):
        self.quit()
    on_quit = on_quit_button_clicked

    def quit(self):
        ctx.settings.save()
        ctx.logger.log_file.close()
        gtk.main_quit()

    @classmethod
    def on_about(cls, sender, arg=None):
        """Show the about dialog"""
        dialog = gtk.AboutDialog()
        dialog.set_program_name('')
        dialog.set_copyright(get_copyright())
        dialog.set_authors(AUTHORS)
        dialog.set_artists(ARTISTS)
        dialog.set_license(LICENSE)
        logo = gtk.gdk.pixbuf_new_from_file(
            path.join(ctx.context['root_path'], 'shared',
            'icons', 'logo_small.png'))
        dialog.set_logo(logo)
        dialog.set_comments('Newsletter Verwaltungssystem, zum erstellen und '
                            'verschicken von elektronischen Newslettern via '
                            'E-Mail.')
        dialog.set_website('http://webshox.org')
        if dialog.run():
            dialog.destroy()
        ctx.logger.debug('about dialog initalized')
