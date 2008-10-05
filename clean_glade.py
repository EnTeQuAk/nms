#-*- coding: utf-8 -*-
import os
from StringIO import StringIO

DELETE_IT = [
    '<property name="events">GDK_POINTER_MOTION_MASK | GDK_POINTER_MOTION_HINT_MASK | GDK_BUTTON_PRESS_MASK | GDK_BUTTON_RELEASE_MASK</property>',
    '<property name="events">GDK_POINTER_MOTION_MASK | GDK_POINTER_MOTION_HINT_MASK | GDK_BUTTON_MOTION_MASK | GDK_BUTTON_PRESS_MASK | GDK_BUTTON_RELEASE_MASK</property>'
]


def clean_glade():
    path = os.path.join(os.path.dirname(__name__), 'nms', 'shared', 'ui', 'core.glade')
    f = open(path)
    temp = StringIO(f.read())
    new = ''
    f.close()
    for line in temp.readlines():
        if not line.strip() in DELETE_IT:
            new += '%s' % line
    f = open(path, 'w')
    f.write(new)
    f.close()


if __name__ == '__main__':
    clean_glade()
