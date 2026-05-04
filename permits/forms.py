from django import forms
from django.core.exceptions import ValidationError

from .models import GovernmentID, WorkPermitRequest


class WorkPermitForm(forms.ModelForm):
    work_types_multi = forms.MultipleChoiceField(choices=WorkPermitRequest.WORK_TYPE_CHOICES, widget=forms.CheckboxSelectMultiple, required=False, label='Description of Work')
    ppe_items_multi = forms.MultipleChoiceField(choices=WorkPermitRequest.PPE_CHOICES, widget=forms.CheckboxSelectMultiple, required=False, label='PPE Required')

    class Meta:
        model = WorkPermitRequest
        fields = [
            'valid_from', 'valid_to', 'location', 'hazards', 'precautions', 'legal_requirements', 'persons_to_notify', 'contractor_name',
            'contact_person', 'country_code', 'phone_number', 'department', 'shift_start', 'shift_end', 'exact_location', 'other_requirement',
        ]
        widgets = {
            'valid_from': forms.DateInput(attrs={'type': 'date'}),
            'valid_to': forms.DateInput(attrs={'type': 'date'}),
            'shift_start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'shift_end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'hazards': forms.Textarea(attrs={'rows': 2}),
            'precautions': forms.Textarea(attrs={'rows': 2}),
            'legal_requirements': forms.Textarea(attrs={'rows': 2}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('valid_from') and cleaned_data.get('valid_to') and cleaned_data['valid_from'] > cleaned_data['valid_to']:
            raise ValidationError('Permit valid-to date must be greater than or equal to valid-from date.')
        if cleaned_data.get('shift_start') and cleaned_data.get('shift_end') and cleaned_data['shift_start'] >= cleaned_data['shift_end']:
            raise ValidationError('Shift end must be after shift start.')
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.work_types = '|'.join(self.cleaned_data.get('work_types_multi', []))
        instance.ppe_items = '|'.join(self.cleaned_data.get('ppe_items_multi', []))
        if commit:
            instance.save()
        return instance


class GovernmentIDForm(forms.ModelForm):
    class Meta:
        model = GovernmentID
        fields = ['id_type', 'id_number', 'id_photo', 'visitor_photo']
        widgets = {
            'id_photo': forms.FileInput(attrs={'accept': '.jpeg,.jpg,.png,.pdf,image/jpeg,image/png,application/pdf'}),
            'visitor_photo': forms.FileInput(attrs={'accept': '.jpeg,.jpg,.png,image/jpeg,image/png'}),
        }
