from django import forms
from django.contrib.auth.models import User
from .models import Profile
import re


# Create your models here.

class LoginForm(forms.Form):
    username = forms.CharField(label="Eamil/Username")
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password',
                               widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password',
                                widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']

    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError('Email already in use.')
        return data


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        data = self.cleaned_data['email']
        qs = User.objects.exclude(id=self.instance.id)\
                         .filter(email=data)
        if qs.exists():
            raise forms.ValidationError('Email already in use.')
        return data


class DateInput(forms.DateInput):
    input_type = 'date'


class ProfileEditForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['phone', 'country', 'date_of_birth', 'photo']
        widgets = {
            'date_of_birth': DateInput()
        }

    def is_valid_phone(self, phone):
        return re.match("^01[0125][0-9]{8}$", phone)

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not self.is_valid_phone(phone):  # You create this function
            # self.add_error('phone', "Invalid Egyptian phone number format.")
            raise forms.ValidationError(
                'Invalid phone format.')
        return phone
