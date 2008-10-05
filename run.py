#-*- coding: utf-8 -*-
import gtk
import sys
import nms
from nms import ctx
from nms.application import run, init_ctx
from werkzeug import script


def shell_env():
    ctx = init_ctx()
    from nms.database import db
    return {
        'ctx': init_ctx(),
        'db': db,
        'nms': nms
    }

action_shell = script.make_shell(shell_env,
    ('\nWelcome to the interactive shell environment of NMS!\n'
     '\n'
     'You can use the following predefined objects: app, ctx, nms, db.\n'))


def run_app():
    try:
        run()
    except KeyboardInterrupt:
        pass
    sys.exit(0)
    print "Thanks for using!"

action_run = lambda: run_app()


if __name__ == '__main__':
    script.run()
