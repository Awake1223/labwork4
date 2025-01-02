from django import forms
from .models import Article

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'author', 'year']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Название'}),
            'author': forms.TextInput(attrs={'placeholder': 'Автор'}),
            'year': forms.NumberInput(attrs={'placeholder': 'Год'}),
        }