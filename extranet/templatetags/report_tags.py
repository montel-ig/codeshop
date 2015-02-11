from django import template


register = template.Library()


@register.inclusion_tag('extranet/show_hours_report.html')
def show_hours_report(report):
    return {'report': report}
