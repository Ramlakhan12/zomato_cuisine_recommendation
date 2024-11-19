from django import forms
from .models import Order

class OrderHistoryForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('restaurant',)
        labels = {
            'restaurant': 'Previous Order (Restaurant Name)',
        }
        help_texts = {
            'restaurant': 'Enter the name of a restaurant you\'ve previously ordered from.',
        }
