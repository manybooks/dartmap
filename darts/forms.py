from django import forms

class SourceUrlForm(forms.Form):
    url = forms.URLField(required=True)
    recursion = forms.BooleanField()
