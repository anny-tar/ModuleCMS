from django import template

register = template.Library()

SECTION_BADGE_COLORS = {
    'hero':         '#6366f1',
    'text':         '#64748b',
    'counters':     '#0891b2',
    'cards':        '#0284c7',
    'team':         '#7c3aed',
    'steps':        '#059669',
    'table':        '#d97706',
    'chart_pie':    '#dc2626',
    'form':         '#db2777',
    'faq':          '#65a30d',
    'testimonials': '#9333ea',
    'contacts':     '#0d9488',
}


@register.filter
def section_color(section):
    return SECTION_BADGE_COLORS.get(section.type, '#94a3b8')
