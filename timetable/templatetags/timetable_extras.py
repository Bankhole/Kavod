from django import template

register = template.Library()


@register.filter
def get_item(mapping, key):
    """Look up a dict value by key from a template (dicts don't support subscript access)."""
    if mapping is None:
        return None
    return mapping.get(key)
