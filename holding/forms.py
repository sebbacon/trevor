from django import forms

from models import WaitingList

class WaitingListForm(forms.Form):
    email = forms.EmailField(required=True)

    def save(self):
        return WaitingList(email=self.cleaned_data['email'])
