from django import forms
from .models import Project, CampaignImages


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'title', 'details', 'target', 'category',
            'campaign_start_date', 'campaign_end_date',
            'tags',
        ]

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("campaign_start_date")
        end_date = cleaned_data.get("campaign_end_date")
        if end_date <= start_date:
            raise forms.ValidationError(
                'End date should be greater than start date.')
            # msg = u"End date should be greater than start date."
            # self._errors["end_date"] = self.error_class([msg])
        return cleaned_data


class ImagesForm(forms.ModelForm):
    images = forms.ImageField(label='Image')

    class Meta:
        model = CampaignImages
        fields = ('images', )
