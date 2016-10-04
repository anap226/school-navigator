from schools import forms as schools_forms
from schools import models as schools_models

from django.shortcuts import render
from django.http import Http404

from django.utils import timezone


def survey_form(request, hash):
    try:
        pk = schools_models.SchoolProfile.decode_url(hash)
    except:
        raise Http404("Survey does not exist")

    profile = schools_models.SchoolProfile.objects.get(pk=pk)

    if profile.overdue():
        raise Http404("Survey Period Has Closed")

    if request.POST:
        print(request.FILES)
        form = schools_forms.SchoolProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            survey = form.save(commit=False)
            survey.school = profile.school
            survey.submitted_at = timezone.now()
            survey.save()
    else:
        form = schools_forms.SchoolProfileForm(instance=profile)
    context = {
        'form': form,
    }
    school = profile.school
    return render(request, 'survey_form.html', {'form': form, 'school': school})
