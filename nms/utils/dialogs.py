#-*- coding: utf-8 -*-
import gtk


def _clear_gtk_entry_on_activate_event(widget):
    if widget.get_text():
        widget.set_text('')


def new_recipient_dialog(title, description):
    dialog = gtk.Dialog(title=title)
    dialog.set_modal(True)
    dialog.set_position(gtk.WIN_POS_CENTER)
    dialog.set_border_width(6)
    dialog.set_has_separator(False)
    dialog.set_resizable(False)

    # Buttons
    cancel_button = dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
    ok_button = dialog.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
    ok_button.set_flags(gtk.CAN_DEFAULT)
    ok_button.grab_default()
    ok_button.set_sensitive(False)

    # Label
    label = gtk.Label(description)
    label.set_line_wrap(True)
    #label.set_use_markup(True)
    dialog.vbox.pack_start(label, True, True, 0)

    # Textbox
    name = gtk.Entry()
    email = gtk.Entry()
    name.set_text(u'Empfänger Name')
    email.set_text('E-Mail Adresse')
    name.connect('activate', _clear_gtk_entry_on_activate_event)
    email.connect('activate', _clear_gtk_entry_on_activate_event)
    dialog.vbox.pack_start(name, True, True, 8)
    dialog.vbox.pack_start(email, True, True, 8)

    def entry_key_release_event(widget, event, data = None):
        if widget.get_text() == "":
            ok_button.set_property("sensitive", False)
        else:
            ok_button.set_property("sensitive", True)
            if event.hardware_keycode == 13:
                dialog.response(gtk.RESPONSE_OK)

    name.connect('key-release-event', entry_key_release_event)
    email.connect('key-release-event', entry_key_release_event)

    dialog.show_all()
    # Anzeigen und zurück geben
    if dialog.run() == gtk.RESPONSE_OK:
        name, email = name.get_text(), email.get_text()
        dialog.destroy()
        return (name, email)
    else:
        dialog.destroy()
        return None
