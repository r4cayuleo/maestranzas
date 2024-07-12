from django import forms
from .models import Material, Location
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['name', 'description', 'quantity', 'location']

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'max_capacity']

class LocationSelectForm(forms.Form):
    location = forms.ModelChoiceField(queryset=Location.objects.all())

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class SearchForm(forms.Form):
    location = forms.ModelChoiceField(queryset=Location.objects.all(), required=False)
    name = forms.CharField(max_length=100, required=False)
