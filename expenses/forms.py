from django import forms
from .models import Expense, Category, UserProfile

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'amount', 'description', 'date', 'document']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'document': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['logo', 'currency']
