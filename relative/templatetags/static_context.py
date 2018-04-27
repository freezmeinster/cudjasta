from django import template
from django.apps import apps
from django.templatetags.static import static

register = template.Library()

class StaticNode(template.Node):
    def __init__(self, varname=None, path=None):
        if path is None:
            raise template.TemplateSyntaxError(
                "Static template nodes must be given a path to return.")
        self.path = path
        self.varname = varname

    def url(self, context):
        path = self.path.resolve(context)
        return self.handle_simple(path)

    def render(self, context):
        tenant = context['request'].META.get("HTTP_TENANT")
        url = self.url(context)
        if tenant:
            url = "/%s" % tenant + url
        if self.varname is None:
            return url
        context[self.varname] = url
        return ''

    @classmethod
    def handle_simple(cls, path):
        if apps.is_installed('django.contrib.staticfiles'):
            from django.contrib.staticfiles.storage import staticfiles_storage
            return staticfiles_storage.url(path)
        else:
            return urljoin(PrefixNode.handle_simple("STATIC_URL"), path)

    @classmethod
    def handle_token(cls, parser, token):
        """
        Class method to parse prefix node and return a Node.
        """
        bits = token.split_contents()

        if len(bits) < 2:
            raise template.TemplateSyntaxError(
                "'%s' takes at least one argument (path to file)" % bits[0])

        path = parser.compile_filter(bits[1])

        if len(bits) >= 2 and bits[-2] == 'as':
            varname = bits[3]
        else:
            varname = None

        return cls(varname, path)

@register.tag
def get_static(parser, token):
    return StaticNode.handle_token(parser, token)
