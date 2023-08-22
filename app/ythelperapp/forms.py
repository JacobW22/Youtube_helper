from django.contrib.auth.forms import UserCreationForm
from django import forms 

from .models import user_data_storage, User

import re

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username','email','password1', 'password2')


class LoginUserForm(forms.Form):
    email = forms.EmailField(max_length = 254)
    password = forms.CharField()

    
    def clean_email(self):
        email = self.cleaned_data['email'].lower()

       
        account = User.objects.filter(email__exact=email).first()

        if account:
            return email
        else:
            raise forms.ValidationError('Email is invalid')
    
      
class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username','email')

    save_history = forms.BooleanField(required=False)


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
        account.save_history = self.cleaned_data['save_history']

        if commit:
            account.save()

            storage = user_data_storage.objects.get(
                user=User.objects.get(username=self.cleaned_data['username'])
            )

            storage.save_history = self.cleaned_data['save_history']
            storage.object_name = str(self.cleaned_data['username'])+" storage"
            storage.save()

        return account
    
class StartTaskForm(forms.Form):
    url = forms.CharField(max_length=273)

    def clean_youtube_url(self):
        url = self.cleaned_data['url']
        # Remove leading/trailing spaces
        youtube_url = url.strip()

        # Regular expression pattern for matching YouTube URLs
        youtube_url_pattern = (
            r'^(https?://)?(www\.)?'
            r'(youtube\.com|youtu\.be)/'
            r'((watch\?v=|playlist\?list=)([a-zA-Z0-9_-]+))'
        )

        # Match the URL pattern
        match = re.match(youtube_url_pattern, youtube_url)

        if match:
            try:
                url = url.split("list=", 1)[1]
                playlist_id = url.split("&", 1)[0]
            except Exception:
                raise forms.ValidationError("Invalid URL")
            
            return playlist_id
        
        # Invalid YouTube URL, return None or raise an error as needed
        raise forms.ValidationError("Invalid URL")
    

    def clean(self):
        cleaned_data = super().clean()
        # Call the custom cleaning method for 'url' field
        video_id = self.clean_youtube_url()
        # Update the cleaned data with the extracted video ID
        cleaned_data['url'] = video_id
        return cleaned_data