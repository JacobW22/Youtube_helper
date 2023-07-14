from django.contrib.auth.forms import UserCreationForm
from django import forms 
from django.contrib.auth.models import User
from .models import user_data_storage, User

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username','email','password1', 'password2')


        
class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username','email')



    def clean_email(self):
        email = self.cleaned_data['email'].lower()

        try: 
            account = User.objects.exclude(pk=self.instance.pk).get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(f'Email {email} is already in use')
    

    def clean_username(self):
        username = self.cleaned_data['username']

        try: 
            account = User.objects.exclude(pk=self.instance.pk).get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(f'Username {username} is already in use')
    


    def save(self, commit=True):
        account = super(UpdateUserForm, self).save(commit=False)
        account.username = self.cleaned_data['username']
        account.email = self.cleaned_data['email']

        if commit:
            account.save()

            storage = user_data_storage.objects.get(
                user=User.objects.get(username=self.cleaned_data['username'])
            )

            storage.object_name = str(self.cleaned_data['username'])+" storage"
            storage.save()

        return account