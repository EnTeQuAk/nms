# -*- encoding: utf-8 -*-
from os import path
import gtk
import pango
from gtk import glade
from nms import ctx


def gtk_threadsafe(func):
    """
    Dekorator for making functions gtk-threadsafe
    """
    def wrapper(*args, **kwargs):
        gtk.gdk.threads_enter()
        result = func(*args, **kwargs)
        gtk.gdk.threads_leave()
        return result

    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__ = func.__doc__
    return wrapper


def scrolled(widget, shadow=gtk.SHADOW_NONE, with_viewport=True, height=None):
    window = gtk.ScrolledWindow()
    window.set_shadow_type(shadow)
    window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    if with_viewport:
        window.add_with_viewport(widget)
    else:
        window.add(widget)
    if height is not None:
        window.set_property('height-request', height)
    return window


class WidgetProxy(object):
    """
    Class for easier access of a widgettree.
    Basically, it is just synatctic sugar.
    But sugar is nearly as good as caffeine.
    """

    def __init__(self, wtree):
        """
        The contructor.
        wtree
            an xml-widgettree, as returned by gtk.glade.XML()
        """
        self.__wtree = wtree

    def __getattr__(self, name):
        """
        Instead of wtree.get_widget('mywidget')
        one can now use widgets.mywidget
        """
        return self[name]

    def __getitem__(self, name):
        """
        Instead of wtree.get_widget('mywidget')
        one can now use widgets['mywidget']
        """
        widget = self.__wtree.get_widget(name)
        if not widget:
            raise AttributeError("No widget with the name '%s'" % name)
        else:
            return widget


class BaseWindow(object):
    """
    Baseclass for Windows
    """

    def __init__(self, wname, parent=None, filename=None, pkgname=None):
        # if packagename is not given, locate the file inside the package
        gpath = ctx.context['glade_path']
        if pkgname is None:
            self._wtree = gtk.glade.XML(path.join(gpath, filename), wname)
        else:
            data = resource_string(pkgname, filename)
            self._wtree = gtk.glade.xml_new_from_buffer(
                data, len(data), wname)

        # create widgetproxy for easier access of the widgets
        self._widgets = WidgetProxy(self._wtree)
        # mainwindow
        self._window = self.widgets[wname]

        if parent:
            self._window.set_transient_for(parent)

        # try to connect all methods, which start with 'on_' to signals
        dct = dict((name, getattr(self, name)) for name in dir(self.__class__)
                                               if name.startswith('on_'))
        self._wtree.signal_autoconnect(dct)

    def show(self):
        """
        shows the window
        """
        self.window.show()

    def hide(self):
        """
        hides the window
        """
        self.window.hide()

    def destroy(self):
        """destroys the window"""
        self.window.destroy()

    window = property(lambda self: self._window,
                      doc="The window widget")

    widgets = property(lambda self: self._widgets,
                       doc="the widgets collection")


class BaseDialog(BaseWindow):
    """
    Baseclass for Dialogs
    """

    def run(self):
        """
        Run the Window as a dialog.
        `get_response_data` is called if `gtk.RESPONSE_OK` is
        returned elsse `response_id` is returned.
        """
        response_id = self.window.run()
        self.window.hide()
        if response_id == gtk.RESPONSE_OK:
            return self.get_response_data()
        else:
            return None

    def get_response_data(self):
        """
        Override to let the run-method return something usefull.
        """
        raise NotImplementedError('Abstract Method not Implemented')


class TextBuffer(gtk.TextBuffer):

    def __init__(self):
        gtk.TextBuffer.__init__(self)
        #: init all style tags
        self._init_tags()

    def _init_tags(self):
        self.create_tag('bold', weight=pango.WEIGHT_BOLD)
        self.create_tag('italic', style=pango.STYLE_ITALIC)
        self.create_tag('underline', underline=pango.UNDERLINE_SINGLE)
        self.create_tag('strikethrough', strikethrough=True)

    def get_selection_iters(self):
        # init
        start, end = None, None

        # get the selection bounds
        bounds = self.get_selection_bounds()
        if bounds:
            # there is a selection so we use it
            start, end = bounds
        else:
            # there is no selection so just get the cursor mark
            cursor_mark = self.get_insert()
            start = end = self.get_iter_at_mark(cursor_mark)

        return start, end

    def toggle_wrap_text(self, iters=None, type=None):
        if type is None:
            # we can't toggle non typed styles
            return
        if iters is not None:
            only_selection = False
            start, end = iters
        else:
            only_selection = True
            start, end = self.get_selection_iters()

        tag = self.tag_table.lookup(type)
        if self.get_has_selection():
            if start.has_tag(tag):
                self.remove_tag(tag, start, end)
            else:
                self.apply_tag(tag, start, end)
        else:
            if not only_selection:
                if start.has_tag(tag):
                    self.remove_tag(tag, start, end)
                else:
                    self.apply_tag(tag, start, end)

    def modify_selection(self, callback, reselect=True):
        """Get the active selection and modify it."""
        start, end = self.get_selection_bounds() or (None, None)
        if start != end:
            text = self.get_text(start, end)
            self.delete(start, end)
            new_text = callback(self, text)
            if new_text:
                mark = self.create_mark(None, start, True)
                self.insert(end, new_text)
                if reselect:
                    self.select_range(self.get_iter_at_mark(mark), end)
                self.delete_mark(mark)
            else:
                self.insert_at_cursor(callback(self, ''))

    def on_copy(self, sender, arg=None):
        self.copy_clipboard(ctx.clipboard)
        self.stop_signal(sender, 'copy-clipboard')

    def on_cut(self, sender, arg=None):
        self.cut_clipboard(ctx.clipboard, True)
        self.stop_signal(sender, 'cut-clipboard')

    def on_paste(self, sender, arg=None):
        self.paste_clipboard(ctx.clipboard, None, True)
        self.stop_signal(sender, 'paste-clipboard')

    def on_delete(self, sender, arg=None):
        self.modify_selection(lambda *a: '')

    def stop_signal(self, sender, signal):
        if isinstance(sender, gtk.TextView):
            sender.emit_stop_by_name(signal)
