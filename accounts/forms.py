from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from .models import Account, Payroll
from django import forms
from django.forms import ModelForm, widgets

class CustomUserCreationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given email and
    password.
    """

    def __init__(self, *args, **kargs):
        super(CustomUserCreationForm, self).__init__(*args, **kargs)
        #del self.fields['username']
        self.fields['email'].widget.attrs.update({'class' : 'form-control'})
        self.fields['password1'].widget.attrs.update({'class' : 'form-control'})
        self.fields['password2'].widget.attrs.update({'class' : 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class' : 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class' : 'form-control'})
        self.fields['address'].widget.attrs.update({'class' : 'form-control'})
        self.fields['contact_number'].widget.attrs.update({'class' : 'form-control'})
        self.fields['profile_pic'].widget.attrs.update({'class' : 'form-control'})
        self.fields['about_me'].widget.attrs.update({'class' : 'form-control'})
    class Meta:
        model = Account
        fields = ('email', 'password1', 'password2', 'first_name', 'last_name', 'address', 'contact_number', 'profile_pic', 'about_me')

class CustomUserChangeForm(UserChangeForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    def __init__(self, *args, **kargs):
        super(CustomUserChangeForm, self).__init__(*args, **kargs)
        #del self.fields['username']
        self.fields['email'].widget.attrs.update({'class' : 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class' : 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class' : 'form-control'})
        self.fields['address'].widget.attrs.update({'class' : 'form-control'})
        self.fields['contact_number'].widget.attrs.update({'class' : 'form-control'})
        self.fields['profile_pic'].widget.attrs.update({'class' : 'form-control'})
        self.fields['about_me'].widget.attrs.update({'class' : 'form-control'})

    class Meta:
        model = Account
        fields = ('email', 'first_name', 'last_name', 'address', 'contact_number', 'profile_pic', 'about_me', 'password')

# class CustomPasswordChangeForm(PasswordChangeForm):
#     def __init__(self, *args, **kwargs):
#         super(CustomPasswordChangeForm, self).__init__(*args, **kwargs)
#         self.fields['password'].widget.attrs.update({'class' : 'form-control'})
#     class Meta:
#         model = Account
#         fields = ('password',)

#Login form
class LoginForm(forms.Form):
    email = forms.EmailField(max_length=100, label="Email address", widget=forms.TextInput(attrs={'class': 'form-control',}))
    password = forms.CharField(min_length=6, label="Password", widget=forms.PasswordInput(attrs={'class': 'form-control',}))

#Add payroll form
class AddPayrollForm(ModelForm):
    class Meta:
        model = Payroll
        fields = ['employee', 'date', 'description']
        widgets = {
            'date': widgets.DateTimeInput(attrs={'type': 'date', 'class':'form-control'}),
        }

    def __init__(self, *args, **kargs):
        super(AddPayrollForm, self).__init__(*args, **kargs)
        self.fields['description'].widget.attrs.update({'class' : 'form-control'})
        self.fields['employee'].widget.attrs.update({'class' : 'form-control'})