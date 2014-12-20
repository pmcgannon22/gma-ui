from django import forms
from bootstrap3_datetime.widgets import DateTimePicker
from datetime import date

class LoginForm(forms.Form):
    username = forms.CharField()
    username.widget = forms.TextInput(attrs={
            'placeholder':'Username/Phone Number',
            'required':'',
            'autofocus':'',
            'class':'form-control',
            })
    password = forms.CharField()
    password.widget = forms.PasswordInput(attrs={
            'class':'form-control',
            'placeholder':'Password',
            'required':''
            })

class MessageForm(forms.Form):
    def __init__(self, *args, **kwargs):
        members = kwargs.pop('members').items()
        created = kwargs.pop('created')
        super(MessageForm, self).__init__(*args, **kwargs)
        self.fields['sent_by'].choices = members
        self.fields['max_likes'].initial = len(members)
        self.fields['start_date'].initial = date.fromtimestamp(float(created))

    random = forms.BooleanField(label="Randomize", required=False)
    img = forms.BooleanField(label="Contains image", required=False)
    min_likes = forms.IntegerField(initial=0, widget=forms.TextInput(attrs={
                    'class':'form-control','placeholder':'Min.','type':'number'}))
    max_likes = forms.IntegerField(widget=forms.TextInput(attrs={
                    'class':'form-control','placeholder':'Max.', 'type':'number'}))

    limit = forms.IntegerField(min_value=0, max_value=150, initial=150, label="Limit (max. 150)", widget=forms.TextInput(attrs={
                    'class':'form-control', 'placeholder':'Limit', 'type':'number'}))

    start_date = forms.DateField(
        widget=DateTimePicker(options={"format": "MM/DD/YYYY",
                                       "pickTime": False}), required=False)
    end_date = forms.DateField(initial=date.today,
        widget=DateTimePicker(options={"format": "MM/DD/YYYY",
                                       "pickTime": False,
                                       "showToday": True}))

    sent_by = forms.MultipleChoiceField(label="Sender(s)", widget=forms.SelectMultiple(
                                            attrs={'class':'selectpicker'}))
    sort_by = forms.ChoiceField(label="Sort", choices=[('n_likes','Likes'), ('author','Group by Sender'), ('created','Date')], initial='Likes',
                                            widget=forms.Select(attrs={'class': 'selectpicker'}))
    sort_order = forms.BooleanField(label="Descending", initial=True, required=False)

    text_contains = forms.CharField(label='Text Contains', widget=forms.TextInput(attrs={
                    'class':'form-control', 'type':'text'}), required=False)

    text_not_contain = forms.CharField(label='Does Not Contain', widget=forms.TextInput(attrs={
                        'class':'form-control', 'type':'text'}), required=False)
