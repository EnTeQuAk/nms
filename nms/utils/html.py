#-*- coding: utf-8 -*-
from werkzeug import escape
from xml.sax.saxutils import quoteattr


#: set of tags that don't want child elements.
EMPTY_TAGS = set(['br', 'img', 'area', 'hr', 'param', 'meta', 'link', 'base',
                  'input', 'embed', 'col', 'frame', 'spacer'])

def _build_html_tag(tag, attrs):
    """Build an HTML opening tag."""
    attrs = u' '.join(iter(
        u'%s=%s' % (k, quoteattr(unicode(v)))
        for k, v in attrs.iteritems()
        if v is not None
    ))
    return u'<%s%s%s>' % (
        tag, attrs and ' ' + attrs or '',
        tag in EMPTY_TAGS and ' /' or ''
    ), tag not in EMPTY_TAGS and u'</%s>' % tag or u''


class PangoHTMLRenderer(object):

    tag_mapping = {
        'bold': {
            'tag': u'strong',
        },
        'italic': {
            'tag': u'em',
        },
        'underline': {
            'tag': u'ins',
        },
        'strikethrough': {
            'tag': u'del',
        },
    }

    def __init__(self, buffer):
        self.buffer = buffer

    def get_tags(self):
        tagdict = {}

        for pos in range(self.buffer.get_char_count()):
            iter = self.buffer.get_iter_at_offset(pos)
            for tag in iter.get_tags():
                if tagdict.has_key(tag):
                    if tagdict[tag][-1][1] == pos - 1:
                        tagdict[tag][-1] = (tagdict[tag][-1][0], pos)
                    else:
                        tagdict[tag].append((pos, pos))
                else:
                    tagdict[tag] = [(pos, pos)]
        return tagdict

    def get_text (self, se_callback=None):
        if se_callback is None:
            tm = self.tag_mapping
            se_callback = lambda k,v: _build_html_tag(
                tm[k.get_property('name')]['tag'],
                tm[k.get_property('name')].get('attrs', {}))
        tagdict = self.get_tags()
        buf = self.buffer
        text = buf.get_text(buf.get_start_iter(), buf.get_end_iter())
        cuts = {}

        for k, v in tagdict.items():
            start_tag, end_tag = se_callback(k, v)
            for start, end in v:
                if start in cuts:
                    cuts[start].append(start_tag)
                else:
                    cuts[start] = start_tag

                if (end+1) in cuts:
                    cuts[end+1] = [end_tag] + cuts[end+1]
                else:
                    cuts[end+1] = [end_tag]

        last_pos = 0
        outbuff = u''
        cut_indices = cuts.keys()
        cut_indices.sort()
        for c in cut_indices:
            if not last_pos == c:
                outbuff += text[last_pos:c]
                last_pos = c
            for tag in cuts[c]:
                outbuff += tag
        outbuff += text[last_pos:]
        return outbuff


class PangoPlainRenderer(PangoHTMLRenderer):

    tag_mapping = {
        'bold': {
            'tag': u'**'
        },
        'italic': {
            'tag': u'*'
        },
        'underline': {
            'tag': u'_'
        },
        'strikethrough': {
            'tag': u'––'
        }
    }

    def get_text(self):
        tm = self.tag_mapping
        se_callback = lambda k,v: 2*[tm[k.get_property('name')]['tag']]
        outbuf = PangoHTMLRenderer.get_text(self, se_callback)
        return outbuf
