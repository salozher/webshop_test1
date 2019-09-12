from django import forms
from .models import Art



class ArtObjectForm(forms.ModelForm):
    class Meta:
        model = Art
        fields = ('category', 'title', 'description', 'cover', 'price')

    def __init__(self, *args, **kwargs):
        super(ArtObjectForm, self).__init__(*args, **kwargs)
        # self.fields['owner'].queryset = NoviUser.objects.filter(is_employee=True, user=NoviUser.is_employee)
        # self.fields['owner'].queryset = MyUser.objects.filter(is_employee=True)

