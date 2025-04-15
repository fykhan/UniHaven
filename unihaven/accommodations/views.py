import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from accommodations.forms import AccommodationForm, ReservationForm, RatingForm
from datetime import date
from django.core.mail import send_mail

API_BASE_URL = settings.API_BASE_URL

def is_cedars(user):
    return user.is_cedars_staff or user.is_superuser


@login_required
def student_accommodation_list(request):
    response = requests.get(f"{API_BASE_URL}accommodations/")
    accommodations = response.json() if response.status_code == 200 else []
    return render(request, 'list.html', {'accommodations': accommodations, 'is_cedars': request.user.is_cedars_staff})


@login_required
def accommodation_detail(request, pk):
    res = requests.get(f"{API_BASE_URL}accommodations/{pk}/")
    if res.status_code != 200:
        messages.error(request, "Accommodation not found.")
        return redirect('accommodation_list')
    acc = res.json()
    return render(request, 'detail.html', {'accommodation': acc, 'is_cedars': request.user.is_cedars_staff})


@login_required
def create_reservation_view(request):
    acc_id = request.GET.get('accommodation')
    accommodation = {}
    if acc_id:
        res = requests.get(f"{API_BASE_URL}accommodations/{acc_id}/")
        if res.status_code == 200:
            accommodation = res.json()

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data["student"] = request.user.id
            res = requests.post(f"{API_BASE_URL}reservations/", data=data)
            if res.status_code == 201:
                messages.success(request, "Reservation successful.")
                send_mail(
                    subject='UniHaven: Reservation Confirmation',
                    message=f'You are successfully {accommodation.get("title", "accommodations")}\n'
                            f'Time: {data["start_date"]} to {data["end_date"]}\n'
                            f'Thank you for using UniHaven!',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.user.email],
                    fail_silently=True, 
                )
                return redirect('accommodation_list')
            else:
                messages.error(request, "Reservation failed.")
    else:
        form = ReservationForm(initial={'accommodation': acc_id})

    return render(request, 'reserve.html', {'form': form, 'accommodation': accommodation, 'is_cedars': request.user.is_cedars_staff})


@login_required
def cancel_reservation_view(request, pk):
    res = requests.post(f"{API_BASE_URL}reservations/{pk}/cancel/")
    if res.status_code == 200:
        messages.info(request, "Reservation cancelled.")
        send_mail(
            subject='UniHaven: Reservation Cancellation',
            message='Your reservation is successfully cancelled\nThank you for using UniHaven!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
            fail_silently=True,  
        )
    else:
        messages.error(request, "Cancellation failed.")
    return redirect('accommodation_list')


@login_required
def rate_accommodation_view(request):
    acc_id = request.GET.get('accommodation') or request.POST.get('accommodation')
    accommodation = {}
    if acc_id:
        res = requests.get(f"{API_BASE_URL}accommodations/{acc_id}/")
        if res.status_code == 200:
            accommodation = res.json()

    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data['student'] = request.user.id
            res = requests.post(f"{API_BASE_URL}ratings/", data=data)
            if res.status_code == 201:
                messages.success(request, "Thank you! Your rating has been submitted.")
                return redirect('accommodation_list')
            else:
                messages.error(request, "Rating failed.")
    else:
        form = RatingForm(initial={'accommodation': acc_id})

    return render(request, 'rate.html', {'form': form, 'accommodation': accommodation, 'is_cedars': request.user.is_cedars_staff})


@login_required
@user_passes_test(is_cedars)
def create_accommodation_view(request):
    if request.method == 'POST':
        form = AccommodationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data['created_by'] = request.user.id
            data['owner'] = request.user.id
            res = requests.post(f"{API_BASE_URL}accommodations/", data=data)
            if res.status_code == 201:
                messages.success(request, "Accommodation created.")
                return redirect('accommodation_list')
            else:
                messages.error(request, "Creation failed.")
    else:
        form = AccommodationForm()
    return render(request, 'create.html', {'form': form, 'is_cedars': True})


@login_required
@user_passes_test(is_cedars)
def view_all_reservations(request):
    res = requests.get(f"{API_BASE_URL}reservations/")
    reservations = res.json() if res.status_code == 200 else []
    return render(request, 'reservations.html', {'reservations': reservations, 'is_cedars': True})


@login_required
@user_passes_test(is_cedars)
def cedars_cancel_reservation(request, pk):
    res = requests.post(f"{API_BASE_URL}reservations/{pk}/cancel/")
    if res.status_code == 200:
        messages.info(request, "Reservation cancelled by CEDARS.")
    else:
        messages.error(request, "Failed to cancel.")
    return redirect('view_reservations')


@login_required
def my_reservations_view(request):
    res = requests.get(f"{API_BASE_URL}reservations/?student={request.user.id}")
    reservations = res.json() if res.status_code == 200 else []

    today = date.today()
    for r in reservations:
        r["can_rate"] = r["status"] == "completed" or (r["status"] == "confirmed" and r["end_date"] < str(today))

    return render(request, 'my_reservations.html', {'reservations': reservations, 'is_cedars': request.user.is_cedars_staff})


@login_required
@user_passes_test(is_cedars)
def view_all_ratings(request):
    res = requests.get(f"{API_BASE_URL}ratings/")
    ratings = res.json() if res.status_code == 200 else []
    return render(request, 'all_ratings.html', {'ratings': ratings, 'is_cedars': True})
