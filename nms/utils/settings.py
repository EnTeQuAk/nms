#-*- coding: utf-8 -*-
"""
    nms.utils.settings
    ~~~~~~~~~~~~~~~~~~

    :copyright: 2008 by Christopher Grebs.
    :license: BSD, see LICENSE for more details.
"""
from os import path
from base64 import b64encode, b64decode
from nms import ctx


class Base64Data(object):
    pass

class PasswordString(str, Base64Data):
    pass


class Preferences(object):
    """Load and save some preferences into a config file."""

    # 'key': (type, value)
    parameters = {
        'smtp_host':            (str, 'localhost'),
        'smtp_port':            (int, 25),
        'smtp_user':            (str, ''),
        'smtp_password':        (PasswordString, ''),
        'smtp_use_tls':         (int, False),
        'smtp_raise_error':     (int, False),
        'mail_encoding':        (str, 'utf-8'),
        'mail_default_from':    (str, ''),
        'theme_path':           (str, path.join(path.expanduser(
            '~/.nms'), 'themes')),
        'theme_choice':         (str, ''),
        'log_timeformat':       (str, '%H:%M:%S'),
        'debug':                (bool, False),
    }

    def __init__(self):
        self.filename = path.join(ctx.context['home_path'], 'nms.conf')
        self._data = {}
        if path.exists(self.filename):
            f = file(self.filename)
            try:
                for line in f:
                    line = line.strip()
                    if line.startswith('#') or not line:
                        continue
                    p = line.split('=', 1)
                    key = p[0].strip()
                    if key not in self.parameters or len(p) != 2:
                        continue
                    converter, default = self.parameters[key]
                    try:
                        value = converter(p[1].strip())
                    except (TypeError, ValueError):
                        value = default
                    self._data[key] = value
            finally:
                f.close()

    def update(self, *args, **kwargs):
        for key, value in kwargs.iteritems():
            self[key] = value

    def __getitem__(self, key):
        conv = self.parameters[key][0]
        data = self._data.get(key, self.parameters[key][1])
        if Base64Data in conv.__bases__:
            data = b64decode(data)
        return data

    def __setitem__(self, key, value):
        conv = self.parameters[key][0]
        if Base64Data in conv.__bases__:
            value = b64encode(value)
        self._data[key] = conv(value)

    def save(self):
        f = file(self.filename, 'w')
        data = []
        for key, value in sorted(self._data.iteritems()):
            converter, _ = self.parameters.get(key, (None, None))
            value = str(converter(value))
            data.append((key, value))
            f.write('%s = %s\n' % (key, value))
        f.close()
