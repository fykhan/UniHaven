from django import forms

class AccommodationForm(forms.Form):
    title = forms.CharField(max_length=200)
    description = forms.CharField(widget=forms.Textarea)
    property_type = forms.ChoiceField(choices=[
        ('AP', 'Apartment'),
        ('HM', 'House - Entire'),
        ('HR', 'House - Room'),
        ('SH', 'Shared Room'),
    ])
    price = forms.DecimalField(max_digits=8, decimal_places=2)
    beds = forms.IntegerField(min_value=1)
    bedrooms = forms.IntegerField(min_value=0)
    address = forms.CharField(widget=forms.Textarea)
    latitude = forms.DecimalField(max_digits=9, decimal_places=6)
    longitude = forms.DecimalField(max_digits=9, decimal_places=6)
    available_from = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    available_to = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))


class ReservationForm(forms.Form):
    accommodation = forms.IntegerField(widget=forms.HiddenInput())
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))


class RatingForm(forms.Form):
    accommodation = forms.IntegerField(widget=forms.HiddenInput())
    value = forms.IntegerField(min_value=1, max_value=5)
    comment = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False)


class CancelReservationForm(forms.Form):
    # Empty form for "confirm cancel" buttons
    pass
