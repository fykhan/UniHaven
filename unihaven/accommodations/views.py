import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

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
    for accommodation in accommodations:
        accommodation['property_type'] = property_type_map.get(accommodation['property_type'], accommodation['property_type'])
        accommodation['created_at'] = datetime.strptime(accommodation['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M:%S")
    return render(request, 'list.html', {'accommodations': accommodations})


@login_required
def create_accommodation_view(request):
    """
    Handles form submission to create new accommodation via the API.
    """
    if request.method == 'POST':
        data = {
            'title': request.POST.get('title'),
            'description': request.POST.get('description'),
            'property_type': request.POST.get('property_type'),
            'price': request.POST.get('price'),
            'beds': request.POST.get('beds'),
            'bedrooms': request.POST.get('bedrooms'),
            'address': request.POST.get('address'),
            'latitude': request.POST.get('latitude'),
            'longitude': request.POST.get('longitude'),
            'available_from': request.POST.get('available_from'),
            'available_to': request.POST.get('available_to'),
            'owner': request.user.id,
            'created_by': request.user.id
        }

        res = requests.post(request.build_absolute_uri('/api/accommodations/'), json=data)
        if res.status_code == 201:
            messages.success(request, "Accommodation created successfully.")
            return redirect('accommodation_list')
        else:
            messages.error(request, "Failed to create accommodation.")
    return render(request, 'create.html')


@login_required
def create_reservation_view(request):
    """
    Submits a reservation request via the API.
    """
    if request.method == 'POST':
        data = {
            'accommodation': request.POST.get('accommodation'),
            'student': request.user.id,
            'start_date': request.POST.get('start_date'),
            'end_date': request.POST.get('end_date'),
            'status': 'RESERVED'
        }
        res = requests.post(request.build_absolute_uri('/api/reservations/'), json=data)
        if res.status_code == 201:
            messages.success(request, "Reservation successful.")
            return redirect('accommodation_list')
        else:
            messages.error(request, "Reservation failed.")
    return render(request, 'reserve.html')


@login_required
def cancel_reservation_view(request, reservation_id):
    """
    Cancels an existing reservation via the API.
    """
    url = request.build_absolute_uri(f'/api/cancel/{reservation_id}/')
    res = requests.post(url)
    if res.status_code == 200:
        messages.success(request, "Reservation cancelled.")
    else:
        messages.error(request, "Cancellation failed.")
    return redirect('accommodation_list')


@login_required
def rate_accommodation_view(request):
    """
    Submits a rating via the API.
    """
    if request.method == 'POST':
        data = {
            'accommodation': request.POST.get('accommodation'),
            'user': request.user.id,
            'score': request.POST.get('score'),
            'comment': request.POST.get('comment')
        }

        res = requests.post(request.build_absolute_uri('/api/rate/'), json=data)
        if res.status_code == 201:
            messages.success(request, "Thank you for your rating!")
            return redirect('accommodation_list')
        else:
            messages.error(request, "Rating failed. Have you already rated this accommodation?")
    return render(request, 'rate.html')
