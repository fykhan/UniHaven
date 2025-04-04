from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Accommodation, Reservation, Rating
from .forms import AccommodationForm, ReservationForm, RatingForm
from datetime import date
from django.db.models import Avg
from django.contrib import messages

def is_cedars(user):
    return user.is_cedars_staff or user.is_superuser

@login_required
def student_accommodation_list(request):
    accommodations = Accommodation.objects.filter(is_available=True, available_to__gte=date.today())
    return render(request, 'list.html', {'accommodations': accommodations, 'is_cedars': request.user.is_cedars_staff})


@login_required
def accommodation_detail(request, pk):
    acc = get_object_or_404(Accommodation, pk=pk)
    return render(request, 'detail.html', {'accommodation': acc, 'is_cedars': request.user.is_cedars_staff})

@login_required
def create_reservation_view(request):
    acc_id = request.GET.get('accommodation')
    accommodation = get_object_or_404(Accommodation, pk=acc_id)

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.student = request.user
            reservation.accommodation = accommodation
            reservation.status = 'pending'
            reservation.save()
            return redirect('student_accommodations')
    else:
        form = ReservationForm(initial={'accommodation': accommodation.id})

    return render(request, 'reserve.html', {
        'form': form,
        'accommodation': accommodation,
        'is_cedars': request.user.is_cedars_staff
    })

@login_required
def cancel_reservation_view(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, student=request.user)
    if reservation.status in ['confirmed', 'pending']:
        reservation.status = 'cancelled'
        reservation.save()
        messages.info(request, "Reservation cancelled.")
    return redirect('student_accommodations')

@login_required
def rate_accommodation_view(request):
    acc_id = request.GET.get('accommodation') or request.POST.get('accommodation')
    accommodation = get_object_or_404(Accommodation, id=acc_id)

    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.student = request.user
            rating.save()

            new_avg = accommodation.ratings.aggregate(avg=Avg('value'))['avg'] or 0
            accommodation.rating = round(new_avg, 2)
            accommodation.save()

            messages.success(request, "Thank you! Your rating has been submitted.")
            return redirect('student_accommodations')
    else:
        form = RatingForm(initial={'accommodation': acc_id})

    return render(request, 'rate.html', {
        'form': form,
        'accommodation': accommodation,
        'is_cedars': request.user.is_cedars_staff
    })


@login_required
@user_passes_test(is_cedars)
def create_accommodation_view(request):
    if request.method == 'POST':
        form = AccommodationForm(request.POST)
        if form.is_valid():
            acc = form.save(commit=False)
            acc.created_by = request.user
            acc.owner = request.user
            acc.save()
            messages.success(request, "Accommodation created.")
            return redirect('accommodation_list')
    else:
        form = AccommodationForm()
    return render(request, 'create.html', {'form': form, 'is_cedars': True})

@login_required
@user_passes_test(is_cedars)
def view_all_reservations(request):
    reservations = Reservation.objects.all()
    return render(request, 'reservations.html', {'reservations': reservations, 'is_cedars': True})

@login_required
@user_passes_test(is_cedars)
def cedars_cancel_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    reservation.status = 'cancelled'
    reservation.save()
    messages.info(request, "Reservation cancelled by CEDARS.")
    return redirect('view_reservations')

@login_required
def my_reservations_view(request):
    reservations = Reservation.objects.filter(student=request.user).select_related('accommodation').order_by('-created_at')
    today = date.today()

    for res in reservations:
        res.update_status()
        res.can_rate = (
            res.status == "completed" or
            (res.status == "confirmed" and res.end_date < today)
        )

    return render(request, 'my_reservations.html', {
        'reservations': reservations,
        'is_cedars': request.user.is_cedars_staff
    })

@login_required
@user_passes_test(is_cedars)
def view_all_ratings(request):
    ratings = Rating.objects.select_related('student', 'accommodation').order_by('-created_at')
    return render(request, 'all_ratings.html', {
        'ratings': ratings,
        'is_cedars': True
    })
