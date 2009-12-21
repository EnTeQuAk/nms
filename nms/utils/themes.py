#-*- coding: utf-8 -*-
from __future__ import with_statement
import re
from os import path, listdir
from werkzeug import cached_property
from jinja2.loaders import FileSystemLoader
from nms import ctx
from nms.utils.mail import split_email


def find_themes():
    """Return an iterator over all themes available."""
    for name in listdir(ctx.settings['theme_path']):
        full_name = path.join(ctx.settings['theme_path'], name)
        if path.isdir(full_name) and \
            path.isfile(path.join(full_name, 'metadata.txt')):
            yield Theme(name, path.abspath(full_name))


def parse_metadata(string_or_fp):
    """
    Parse the metadata and return it as dict.
    """
    result = {}
    if isinstance(string_or_fp, basestring):
        fileiter = iter(string_or_fp.splitlines(True))
    else:
        fileiter = iter(string_or_fp.readline, '')
    for line in fileiter:
        line = line.strip().decode('utf-8')
        if not line or line.startswith('#'):
            continue
        if not ':' in line:
            key = line.strip()
            value = ''
        else:
            key, value = line.split(':', 1)
        while value.endswith('\\'):
            try:
                value = value[:-1] + fileiter.next().rstrip('\n')
            except StopIteration:
                pass
        try:
            result[str('_'.join(key.lower().split()))] = value.lstrip()
        except UnicodeError:
            continue
    return result


class ThemeLoader(FileSystemLoader):

    def __init__(self):
        self.encoding = 'utf-8'

    @property
    def searchpath(self):
        return ctx.settings['theme_path']

    def get_theme_obj(self, name):
        return Theme(name, path.abspath(path.join(
            self.searchpath, name
        )))

    @property
    def current(self):
        return self.get_theme_obj(ctx.settings['theme_choice'])


class Theme(object):

    def __init__(self, name, path_):
        self.name = name
        self.path = path_

    def render(self, **ctx):
        p = u'%s/%s' % (self.path.split('/')[-1], self.theme_file)
        tmpl = ctx.theme_loader.get_template(p)
        return tmpl.render(**ctx)

    @cached_property
    def token_tree(self):
        with file(path.join(self.path, self.theme_file), 'r') as f:
            tokeniter = ctx.theme_environment.parse(
                f.read(), self.theme_file)
        return tokeniter

    @cached_property
    def metadata(self):
        try:
            fobj = file(path.join(self.path, 'metadata.txt'))
        except IOError:
            return {}
        try:
            metadata = parse_metadata(fobj)
        finally:
            fobj.close()
        return metadata

    @property
    def display_name(self):
        return self.metadata.get('name', self.name)

    @property
    def description(self):
        return self.metadata.get('beschreibung', u'')

    @property
    def author_info(self):
        return split_email(self.metadata.get('autor', u'Unbekannt')) + \
               (self.metadata.get('autor_url', ''),)

    @property
    def author(self):
        x = self.author_info
        return x[0] or x[1]

    @property
    def author_email(self):
        return self.author_info[1]

    @property
    def author_url(self):
        return self.author_info[2]

    @property
    def theme_file(self):
        return self.metadata.get('theme_datei', None)

    @property
    def preview(self):
        return self.metadata.get('vorschau', None)

    @property
    def shared(self):
        data = self.metadata.get('sonstige_dateien', '')
        if data:
            return [x.strip() for x in data.split(',')]
        return []


    def __repr__(self):
        return '<%r %r>' % (
            self.__class__.__name__,
            self.name
        )
    def __str__(self):
        return self.name
