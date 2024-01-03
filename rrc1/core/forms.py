from django import forms


class UserForm(forms.Form):
    username = forms.CharField(max_length=100, required=True)
    password = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput)
    firstname = forms.CharField(max_length=100, required=True)
    lastname = forms.CharField(max_length=100, required=True)

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('client', 'Client'),
    ]

    role = forms.ChoiceField(
        widget=forms.RadioSelect, choices=ROLE_CHOICES, required=True
    )


class UserForm2(forms.Form):
    username = forms.CharField(max_length=100, required=True)
    password = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput)
    firstname = forms.CharField(max_length=100, required=True)
    lastname = forms.CharField(max_length=100, required=True)


class DeviceForm(forms.Form):
    description = forms.CharField(max_length=100, required=True)
    address = forms.CharField(max_length=100, required=True)
    maximum_hourly_energy_consumption = forms.DecimalField(max_digits=10, decimal_places=2, required=True)
