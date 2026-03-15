from django.shortcuts import render, redirect, get_object_or_404
from pages.models import Section
from .models import LeadSubmission


def submit_form(request, section_id):
    if request.method != 'POST':
        return redirect('/')

    section = get_object_or_404(Section, pk=section_id, type='form')
    fields  = section.data.get('fields', [])

    # Сбор данных из POST по именам полей формы
    submission_data = {}
    for field in fields:
        name  = field.get('name')
        value = request.POST.get(name, '').strip()
        if name:
            submission_data[field.get('label', name)] = value

    # Получение IP адреса клиента
    ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0] \
         or request.META.get('REMOTE_ADDR')

    LeadSubmission.objects.create(
        section_id = section_id,
        data       = submission_data,
        ip_address = ip or None,
    )
    return redirect('leads_thanks')


def thanks(request):
    return render(request, 'leads/thanks.html')