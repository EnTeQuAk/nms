#-*- coding: utf-8 -*-
"""
    nms
    ~~~


    :copyright: Christopher Grebs.
    :license: BSD.
"""
import sys
import gtk
import gtk.glade
from os import path, mkdir
from jinja2 import Environment
from nms import ctx
from nms.utils.settings import Preferences
from nms.utils.logger import Logger
from nms.utils.themes import ThemeLoader


def init_ctx():
    first_run = False
    # initialize the context, it stores things like the
    # themes_dir and root_path.
    ctx.context = {}
    ctx.clipboard = gtk.Clipboard()

    # home directory
    home_dir = path.expanduser('~/.nms')
    if not path.exists(home_dir):
        first_run = True
        mkdir(home_dir)
        for dir_ in ('files', 'logs', 'themes'):
            mkdir(path.join(home_dir, dir_))

    root_path = path.abspath(path.dirname(__file__))
    themes_dir = path.join(home_dir, 'themes')
    # setup some settings
    ctx.context.update({
        'root_path': root_path,
        'home_path': home_dir,
        'first_run': first_run,
        'glade_path': path.join(root_path, 'shared', 'ui')
    })
    settings = ctx.settings = Preferences()
    logger = ctx.logger = Logger()
    ctx.theme_loader = ThemeLoader()
    ctx.theme_environment = Environment(loader=ctx.theme_loader)
    from nms.database import metadata
    metadata.create_all()
    return ctx

def run():
    init_ctx()
    from nms.gui import MainWindow
    main = MainWindow()
    main.show()

    gtk.main()

if __name__ == '__main__':
    run()
