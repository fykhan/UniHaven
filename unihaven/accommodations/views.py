import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from .forms import AccommodationForm, ReservationForm, RatingForm
from .models import Accommodation, Reservation, Rating

PROPERTY_TYPES = [
    ('AP', 'Apartment'),
    ('HM', 'House - Entire'),
    ('HR', 'House - Room'),
    ('SH', 'Shared Room'),
]


@login_required
def accommodation_list_view(request):
    """
    Renders the list of accommodations by fetching from the API.
    """
    print("User", request.user)
    api_url = request.build_absolute_uri('/api/accommodations/')
    try:
        response = requests.get(api_url, cookies=request.COOKIES)
        accommodations = response.json() if response.status_code == 200 else []
    except Exception as e:
        messages.error(request, f"Error loading data: {e}")
        accommodations = []
    # Map property_type abbreviations to full names
    
    property_type_map = dict(PROPERTY_TYPES)
    user_reservations = Reservation.objects.filter(student=request.user, status='RESERVED')
    reserved_ids = set(r.accommodation_id for r in user_reservations)

    # Step 2: Add .can_rate and .is_created_by_user to each accommodation
    for acc in accommodations:
        acc['property_type'] = property_type_map.get(acc['property_type'], acc['property_type'])
        acc['created_at'] = datetime.strptime(acc['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M:%S")
        acc['can_rate'] = acc['id'] in reserved_ids and acc['is_available'] is True
    return render(request, 'list.html', {'accommodations': accommodations})

@login_required
def create_accommodation_view(request):
    if request.method == 'POST':
        form = AccommodationForm(request.POST)
        if form.is_valid():
            acc = form.save(commit=False)
            acc.owner = request.user
            acc.created_by = request.user
            acc.save()
            messages.success(request, "Accommodation created.")
            return redirect('accommodation_list')
    else:
        form = AccommodationForm()
    return render(request, 'create.html', {'form': form})


@login_required
def create_reservation_view(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.student = request.user
            reservation.status = 'RESERVED'
            reservation.save()
            messages.success(request, "Reservation submitted.")
            return redirect('accommodation_list')
    else:
        form = ReservationForm()
    
    # Show the selected accommodation if already chosen
    accommodation_id = request.GET.get('accommodation')
    accommodation = None
    if accommodation_id:
        accommodation = Accommodation.objects.filter(id=accommodation_id).first()

    return render(request, 'reserve.html', {
        'form': form,
        'accommodation': accommodation
    })

@login_required
def rate_accommodation_view(request):
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.student = request.user
            if Rating.objects.filter(student=request.user, accommodation=rating.accommodation).exists():
                messages.error(request, "You've already rated this accommodation.")
            else:
                rating.save()
                messages.success(request, "Thank you for your feedback!")
                return redirect('accommodation_list')
    else:
        form = RatingForm()
    return render(request, 'rate.html', {'form': form})


@login_required
def cancel_reservation_view(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, student=request.user)
    accommodation = reservation.accommodation

    if request.method == 'POST':
        form = CancelReservationForm(request.POST, instance=reservation)
        if form.is_valid() and reservation.status == 'RESERVED':
            reservation.status = 'cancelled'
            reservation.save()
            messages.success(request, "Reservation cancelled.")
            return redirect('accommodation_list')
        else:
            messages.error(request, "Cannot cancel this reservation.")
    else:
        form = CancelReservationForm(instance=reservation)

    return render(request, 'cancel.html', {
        'form': form,
        'accommodation': accommodation,
        'reservation': reservation
    })