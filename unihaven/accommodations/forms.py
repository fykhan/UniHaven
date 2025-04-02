from django import forms
from .models import Accommodation, Reservation, Rating

class AccommodationForm(forms.ModelForm):
    class Meta:
        model = Accommodation
        fields = [
            'title', 'description', 'property_type', 'price', 'beds', 'bedrooms',
            'address', 'latitude', 'longitude', 'available_from', 'available_to'
        ]
        widgets = {
            'available_from': forms.DateInput(attrs={'type': 'date'}),
            'available_to': forms.DateInput(attrs={'type': 'date'}),
        }


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['accommodation', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hide accommodation field in UI since it's passed via URL/view
        self.fields['accommodation'].widget = forms.HiddenInput()


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['accommodation', 'value', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['accommodation'].widget = forms.HiddenInput()


class CancelReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = []
