from django import forms

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
