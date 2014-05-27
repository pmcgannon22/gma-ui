from django import forms
from bootstrap3_datetime.widgets import DateTimePicker

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
        super(MessageForm, self).__init__(*args, **kwargs)
        self.fields['sent_by'].choices = members

    random = forms.BooleanField(label="Random", required=False)
    img = forms.BooleanField(label="Contains image", required=False)
    min_likes = forms.IntegerField(widget=forms.TextInput(attrs={
                    'class':'form-control','placeholder':'Min.','type':'number'}))
    max_likes = forms.IntegerField(widget=forms.TextInput(attrs={
                    'class':'form-control','placeholder':'Max.', 'type':'number'}))

    limit = forms.IntegerField(min_value=0, max_value=150, label="Limit (max. 150)", widget=forms.TextInput(attrs={
                    'class':'form-control', 'placeholder':'Limit', 'type':'number'}))

    start_date = forms.DateField(
        widget=DateTimePicker(options={"format": "MM/DD/YYYY",
                                       "pickTime": False}))
    end_date = forms.DateField(
        widget=DateTimePicker(options={"format": "MM/DD/YYYY",
                                       "pickTime": False,
                                       "showToday": True}))

    sent_by = forms.MultipleChoiceField(label="Sender(s)", widget=forms.SelectMultiple(
                                            attrs={'class':'selectpicker'}))
