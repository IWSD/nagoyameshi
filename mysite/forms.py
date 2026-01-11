from django import forms
from .models import Review, Reservation, Shop

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['title', 'rating', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
        }

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['date', 'time', 'num_people']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'num_people': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

class ShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = [
            "name",
            "shop_explanation",
            "near_station",
            "walk_minutes",
            "shop_category_id",
            "price_range",
            "business_hour_start",
            "business_hour_end",
            "address",
            "latitude",
            "longitude",
            "max_reserve_num",
            "img",
        ]