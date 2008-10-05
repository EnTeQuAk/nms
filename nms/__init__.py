#-*- coding: utf-8 -*-
"""
    nms
    ~~~

    :copyright: 2008 by Christopher Grebs.
    :license: BSD.
"""
from __future__ import with_statement
from os.path import join, dirname, abspath
import re
from types import ModuleType
from nms.utils.local import LocalProxy, Local, LocalManager


main_path = join(abspath(dirname(__file__)), '..')

#: local objects
_local = Local()
_local_manager = LocalManager([_local])

#: fake module for context internals
ctx = ModuleType('ctx')
ctx.__doc__ = 'module that holds all context locals'

ctx.context = LocalProxy(_local, 'context')
ctx.settings = LocalProxy(_local, 'settings')
ctx.clipboard = LocalProxy(_local, 'clipboard')
ctx.logger = LocalProxy(_local, 'logger')
ctx.theme_environment = LocalProxy(_local, 'theme_environment')
ctx.theme_loader = LocalProxy(_local, 'theme_loader')


def get_copyright():
    """Return the copyright string for the about dialog."""
    import nms
    return 'Copyright %s' % re.compile(r'^\s+:%s:\s+(.*?)\.$(?m)' % 'copyright') \
            .search(nms.__doc__).group(1).strip()


VERSION = (0, 1)
AUTHORS = ['Christopher Grebs <cg@webshox.org>']
ARTISTS = ['Christian Neumeister <http://crash-grafix.de>']
LICENSE = '''
Copyright (c) 2008 by Christopher Grebs.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.

    * Redistributions in binary form must reproduce the above
      copyright notice, this list of conditions and the following
      disclaimer in the documentation and/or other materials provided
      with the distribution.

    * The names of the contributors may not be used to endorse or
      promote products derived from this software without specific
      prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''


__all__ = ['main_path', 'ctx', 'get_copyright', 'VERSION',
           'AUTHORS', 'TRANSLATORS', 'LICENSE']
