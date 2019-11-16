from django import forms

from .models import Art, CartItem


class ArtObjectForm(forms.ModelForm):
    class Meta:
        model = Art
        fields = ('category', 'title', 'description', 'cover', 'price')

    def __init__(self, *args, **kwargs):
        super(ArtObjectForm, self).__init__(*args, **kwargs)