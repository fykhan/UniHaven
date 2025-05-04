import json
import math
import os
import requests
from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase, Client
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from unittest.mock import patch, MagicMock
from django.contrib.admin.sites import AdminSite
from django.core.exceptions import ValidationError
from random import randint
from api.models import Accommodation, Reservation, Rating, calculate_distance
from api.serializers import AccommodationSerializer, ReservationSerializer, RatingSerializer
from api.views import MeView, AccommodationFilterView, ReservationFilterView, ReservationCancelView
from api.viewsets import AccommodationViewSet, ReservationViewSet, RatingViewSet
from api.admin import AccommodationAdmin, ReservationAdmin, RatingAdmin
from accommodations.forms import AccommodationForm, ReservationForm, RatingForm, CancelReservationForm
from users.models import User, StudentProfile, StaffProfile, AdminProfile

class UniHavenTests(TestCase):
    def setUp(self):
        """Set up test environment with client, users, and sample data."""
        self.client = Client()
        self.api_client = APIClient()
        
        # Create test users
        self.user_student = User.objects.create_user(
            username="student1", password="testpass123", university="HKU",
            is_student=True, email="student1@example.com"
        )
        self.user_staff = User.objects.create_user(
            username="staff1", password="testpass123", university="HKU",
            is_cedars_staff=True, email="staff1@example.com"
        )
        self.user_superuser = User.objects.create_superuser(
            username="admin1", password="testpass123", university="HKU",
            email="admin1@example.com"
        )
        
        # Create test accommodation
        self.accommodation = Accommodation.objects.create(
            title="Test Apartment", description="A nice place", property_type="AP",
            price=1000.00, beds=2, bedrooms=1, address="123 Test St, HK",
            flat_number="1A", floor_number="1", available_from=date.today(),
            available_to=date.today() + timedelta(days=30), created_by=self.user_staff,
            universities_offered=["HKU"], latitude=22.283, longitude=114.135, geo_address="Geo123"
        )
        
        # Create test reservation
        self.reservation = Reservation.objects.create(
            accommodation=self.accommodation, student_name="Student One",
            student_email="student1@example.com", start_date=date.today(),
            end_date=date.today() + timedelta(days=10), created_by=self.user_student,
            status="pending"
        )
        
        # Create test rating
        self.rating = Rating.objects.create(
            accommodation=self.accommodation, student_name="Student One",
            value=4, comment="Great place!", created_by=self.user_student
        )

    def mock_universities_json(self):
        """Mock universities JSON data for testing campus distances."""
        universities_data = {
            "universities": [
                {
                    "code": "HKU",
                    "name": "The University of Hong Kong",
                    "campuses": {
                        "Main Campus": [22.28405, 114.13784],
                        "Sassoon Road Campus": [22.2675, 114.12881],
                        "Swire Institute of Marine Science": [22.20805, 114.26021],
                        "Kadoorie Centre": [22.43022, 114.11429],
                        "Faculty of Dentistry": [22.28649, 114.14426]
                    }
                },
                {
                    "code": "CUHK",
                    "name": "The Chinese University of Hong Kong",
                    "campuses": {"Main Campus": [22.41907, 114.20693]}
                },
                {
                    "code": "HKUST",
                    "name": "The Hong Kong University of Science and Technology",
                    "campuses": {"Main Campus": [22.33584, 114.26355]}
                }
            ]
        }
        with patch("api.models.DATA_PATH", "/tmp/universities.json"):
            with patch("builtins.open", MagicMock()) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(universities_data)
                return universities_data

    # Tests for Users Models
    def test_user_student_creation(self):
        """Test creation and properties of a student user."""
        self.assertTrue(self.user_student.is_student)
        self.assertTrue(hasattr(self.user_student, "student_profile"))
        self.assertEqual(self.user_student.student_profile.university, "HKU")
        self.assertTrue(self.user_student.UID)
        self.assertEqual(self.user_student.get_user_role(), "student")
        self.assertTrue(self.user_student.can_make_reservations())
        self.assertFalse(self.user_student.can_manage_accommodations())

    def test_user_staff_creation(self):
        """Test creation and properties of a staff user."""
        self.assertTrue(self.user_staff.is_cedars_staff)
        self.assertTrue(hasattr(self.user_staff, "staff_profile"))
        self.assertEqual(self.user_staff.staff_profile.university, "HKU")
        self.assertEqual(self.user_staff.get_user_role(), "staff")
        self.assertTrue(self.user_staff.can_manage_accommodations())
        self.assertTrue(self.user_staff.can_view_dashboard())
        self.assertFalse(self.user_staff.can_make_reservations())

    def test_user_superuser_creation(self):
        """Test creation and properties of a superuser."""
        self.assertTrue(self.user_superuser.is_cedars_staff)
        self.assertTrue(self.user_superuser.is_superuser)
        self.assertTrue(self.user_superuser.can_manage_accommodations())
        self.assertTrue(self.user_superuser.can_view_dashboard())

    def test_user_admin_profile_role(self):
        """Test that a user with AdminProfile returns 'admin' role."""
        user = User.objects.create_user(
            username="admin2", password="testpass123", university="HKU",
            email="admin2@example.com"
        )
        AdminProfile.objects.create(user=user)
        self.assertEqual(user.get_user_role(), "admin")

    def test_user_unknown_role(self):
        """Test that a user with no profile returns 'unknown' role."""
        user = User.objects.create_user(
            username="unknown1", password="testpass123", university="HKU",
            email="unknown1@example.com"
        )
        self.assertEqual(user.get_user_role(), "unknown")

    def test_user_validation_error(self):
        """Test that assigning multiple profile roles raises ValidationError."""
        user = User.objects.create_user(
            username="testuser", password="testpass123", university="HKU",
            email="testuser@example.com"
        )
        StudentProfile.objects.create(user=user, university="HKU", UID="1234567890")
        with patch('builtins.hasattr') as mock_hasattr:
            mock_hasattr.side_effect = lambda obj, attr: attr in ['student_profile', 'staff_profile']
            with self.assertRaises(ValidationError) as cm:
                user.clean()
            self.assertEqual(
                str(cm.exception),
                "['A user can only have one profile role (student, staff, admin).']"
            )

    def test_user_clean_multiple_roles(self):
        """Test that creating multiple profile roles raises ValidationError."""
        user = User.objects.create_user(
            username="multi_role", password="testpass123", university="HKU",
            email="multi_role@example.com"
        )
        StudentProfile.objects.create(user=user, university="HKU", UID="1234567890")
        with self.assertRaises(ValidationError) as cm:
            StaffProfile.objects.create(user=user, university="HKU")
            user.clean()
        self.assertEqual(
            str(cm.exception),
            "['A user can only have one profile role (student, staff, admin).']"
        )

    def test_user_str_with_full_name(self):
        """Test user string representation with full name."""
        self.user_student.first_name = "John"
        self.user_student.last_name = "Doe"
        self.user_student.save()
        self.assertEqual(str(self.user_student), "John Doe")

    def test_user_str_without_full_name(self):
        """Test user string representation without full name."""
        self.assertEqual(str(self.user_student), "student1")

    def test_user_student_profile_auto_creation(self):
        """Test automatic creation of StudentProfile on student user save."""
        user = User(
            username="student2", university="HKU", is_student=True,
            email="student2@example.com"
        )
        user.set_password("testpass123")
        self.assertIsNone(user.pk)
        self.assertFalse(hasattr(user, "student_profile"))
        user.save()
        self.assertTrue(hasattr(user, "student_profile"))
        self.assertEqual(user.student_profile.university, "HKU")
        self.assertEqual(user.student_profile.UID, user.UID)

    def test_user_staff_profile_auto_creation(self):
        """Test automatic creation of StaffProfile on staff user save."""
        user = User(
            username="staff2", university="HKU", is_cedars_staff=True,
            email="staff2@example.com"
        )
        user.set_password("testpass123")
        self.assertIsNone(user.pk)
        self.assertFalse(hasattr(user, "staff_profile"))
        user.save()
        self.assertTrue(hasattr(user, "staff_profile"))
        self.assertEqual(user.staff_profile.university, "HKU")

    def test_student_profile_str(self):
        """Test string representation of StudentProfile."""
        self.assertEqual(str(self.user_student.student_profile), "student1 (Student)")

    def test_staff_profile_str(self):
        """Test string representation of StaffProfile."""
        self.assertEqual(str(self.user_staff.staff_profile), "staff1 (CEDARS Staff)")

    def test_admin_profile_str(self):
        """Test string representation of AdminProfile."""
        admin_user = User.objects.create_user(
            username="admin2", password="testpass123", university="HKU",
            email="admin2@example.com"
        )
        admin_profile = AdminProfile.objects.create(user=admin_user)
        self.assertEqual(str(admin_profile), "admin2 (Admin)")

    # Tests for API Models
    @patch("api.models.lookup_coordinates_and_geoaddress")
    def test_accommodation_save(self, mock_lookup):
        """Test saving an accommodation with mocked geolocation."""
        mock_lookup.return_value = (22.283, 114.135, "Geo123")
        self.mock_universities_json()
        accommodation = Accommodation.objects.create(
            title="New Apartment", description="A nice place", property_type="AP",
            price=1000.00, beds=2, bedrooms=1, address="456 New St, HK",
            flat_number="2B", floor_number="2", available_from=date.today(),
            available_to=date.today() + timedelta(days=30), created_by=self.user_staff,
            universities_offered=["HKU"]
        )
        self.assertEqual(accommodation.latitude, 22.283)
        self.assertEqual(accommodation.property_type, "AP")
        self.assertEqual(accommodation.price, 1000.00)
        self.assertEqual(accommodation.beds, 2)
        self.assertEqual(accommodation.bedrooms, 1)
        self.assertEqual(accommodation.address, "456 New St, HK")
        self.assertEqual(accommodation.flat_number, "2B")
        self.assertEqual(accommodation.floor_number, "2")
        self.assertEqual(accommodation.geo_address, "Geo123")
        self.assertIn("HKU - Main Campus", accommodation.campus_distances)
        self.assertEqual(str(accommodation), "New Apartment - Apartment")

    @patch("api.models.lookup_coordinates_and_geoaddress")
    def test_accommodation_lookup_no_suggestions(self, mock_get):
        """Test accommodation save when no geolocation suggestions are returned."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"SuggestedAddress": []}
        mock_get.return_value = mock_response
        with patch("builtins.print"):
            with patch("api.models.lookup_coordinates_and_geoaddress") as mock_lookup:
                mock_lookup.return_value = (None, None, "")
                accommodation = Accommodation.objects.create(
                    title="No Geo Apartment", description="A nice place", property_type="AP",
                    price=1000.00, beds=2, bedrooms=1, address="Unknown St, HK",
                    flat_number="3C", floor_number="3", available_from=date.today(),
                    available_to=date.today() + timedelta(days=30), created_by=self.user_staff,
                    universities_offered=["HKU"]
                )
            self.assertIsNone(accommodation.latitude)
            self.assertIsNone(accommodation.longitude)
            self.assertEqual(accommodation.geo_address, "")

    @patch("api.models.lookup_coordinates_and_geoaddress")
    def test_accommodation_lookup_exception(self, mock_get):
        """Test accommodation save when geolocation lookup raises an exception."""
        mock_get.side_effect = requests.RequestException("Network error")
        with patch("builtins.print"):
            with patch("api.models.lookup_coordinates_and_geoaddress") as mock_lookup:
                mock_lookup.return_value = (None, None, "")
                accommodation = Accommodation.objects.create(
                    title="Error Apartment", description="A nice place", property_type="AP",
                    price=1000.00, beds=2, bedrooms=1, address="Error St, HK",
                    flat_number="4D", floor_number="4", available_from=date.today(),
                    available_to=date.today() + timedelta(days=30), created_by=self.user_staff,
                    universities_offered=["HKU"]
                )
            self.assertIsNone(accommodation.latitude)
            self.assertIsNone(accommodation.longitude)
            self.assertEqual(accommodation.geo_address, "")

    def test_accommodation_average_rating(self):
        """Test calculation of average rating for an accommodation."""
        self.assertEqual(self.accommodation.average_rating(), 4.0)
        Rating.objects.create(
            accommodation=self.accommodation, student_name="Student Two",
            value=2, created_by=self.user_student
        )
        self.assertEqual(self.accommodation.average_rating(), 3.0)

    def test_reservation_status_update(self):
        """Test automatic status updates for a reservation based on dates."""
        # Test completed status
        self.reservation.end_date = date.today() - timedelta(days=1)
        self.reservation.update_status()
        self.assertEqual(self.reservation.status, "completed")

        # Test confirmed status
        self.reservation.status = "pending"
        self.reservation.start_date = date.today()
        self.reservation.end_date = date.today() + timedelta(days=1)
        self.reservation.update_status()
        self.assertEqual(self.reservation.status, "confirmed")

        # Test pending status
        self.reservation.start_date = date.today() + timedelta(days=1)
        self.reservation.update_status()
        self.assertEqual(self.reservation.status, "pending")

        # Test no change for cancelled status
        self.reservation.status = "cancelled"
        self.reservation.update_status()
        self.assertEqual(self.reservation.status, "cancelled")

    def test_reservation_str(self):
        """Test string representation of a reservation."""
        self.assertEqual(str(self.reservation), f"Reservation #{self.reservation.id} - Test Apartment")

    def test_rating_str(self):
        """Test string representation of a rating."""
        self.assertEqual(str(self.rating), "4 stars for Test Apartment")

    def test_calculate_distance(self):
        """Test the calculate_distance function for geographical distance."""
        lat1, lon1 = 22.283, 114.135
        lat2, lon2 = 22.28405, 114.13784
        distance = calculate_distance(lat1, lon1, lat2, lon2)
        R = 6371  # Earth's radius in km
        lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
        lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        expected_distance = R * c
        self.assertAlmostEqual(distance, expected_distance, delta=0.01)

    # Tests for Forms
    def test_accommodation_form_valid(self):
        """Test valid data for AccommodationForm."""
        data = {
            "title": "New Apartment",
            "description": "A nice place",
            "property_type": "AP",
            "price": 1000.00,
            "beds": 2,
            "bedrooms": 1,
            "address": "456 New St, HK",
            "latitude": 22.283,
            "longitude": 114.135,
            "available_from": date.today(),
            "available_to": date.today() + timedelta(days=30)
        }
        form = AccommodationForm(data=data)
        self.assertTrue(form.is_valid())

    def test_reservation_form_valid(self):
        """Test valid data for ReservationForm."""
        data = {
            "accommodation": self.accommodation.id,
            "start_date": date.today(),
            "end_date": date.today() + timedelta(days=10)
        }
        form = ReservationForm(data=data)
        self.assertTrue(form.is_valid())

    def test_rating_form_valid(self):
        """Test valid data for RatingForm."""
        data = {
            "accommodation": self.accommodation.id,
            "value": 5,
            "comment": "Amazing!"
        }
        form = RatingForm(data=data)
        self.assertTrue(form.is_valid())

    def test_rating_form_invalid(self):
        """Test invalid data (rating > 5) for RatingForm."""
        data = {
            "accommodation": self.accommodation.id,
            "value": 6,  # Invalid: > 5
            "comment": "Amazing!"
        }
        form = RatingForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("value", form.errors)

    # Tests for Serializers
    def test_reservation_serializer(self):
        """Test ReservationSerializer output."""
        serializer = ReservationSerializer(self.reservation)
        data = serializer.data
        self.assertEqual(data["student_name"], "Student One")
        self.assertEqual(data["status"], "pending")
        self.assertEqual(data["created_by"], self.user_student.username)

    def test_rating_serializer(self):
        """Test RatingSerializer output."""
        serializer = RatingSerializer(self.rating)
        data = serializer.data
        self.assertEqual(data["value"], 4)
        self.assertEqual(data["comment"], "Great place!")
        self.assertEqual(data["created_by"], self.user_student.username)

    # Tests for Viewsets
    def test_accommodation_viewset_list(self):
        """Test listing accommodations via AccommodationViewSet."""
        self.api_client.force_authenticate(user=self.user_student)
        response = self.api_client.get("/api/accommodations/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Test Apartment")

    def test_accommodation_viewset_create(self):
        """Test creating an accommodation via AccommodationViewSet."""
        self.api_client.force_authenticate(user=self.user_staff)
        data = {
            "title": "New Apartment",
            "description": "A nice place",
            "property_type": "AP",
            "price": "1000.00",
            "beds": 2,
            "bedrooms": 1,
            "address": "456 New St, HK",
            "flat_number": "2B",
            "floor_number": "2",
            "available_from": date.today().isoformat(),
            "available_to": (date.today() + timedelta(days=30)).isoformat(),
            "universities_offered": ["HKU"]
        }
        response = self.api_client.post("/api/accommodations/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Accommodation.objects.count(), 2)

    def test_accommodation_viewset_create_duplicate(self):
        """Test creating a duplicate accommodation fails."""
        self.api_client.force_authenticate(user=self.user_staff)
        data = {
            "title": "Duplicate Apartment",
            "description": "A nice place",
            "property_type": "AP",
            "price": "1000.00",
            "beds": 2,
            "bedrooms": 1,
            "address": self.accommodation.address,
            "flat_number": self.accommodation.flat_number,
            "floor_number": self.accommodation.floor_number,
            "available_from": date.today().isoformat(),
            "available_to": (date.today() + timedelta(days=30)).isoformat(),
            "universities_offered": ["HKU"]
        }
        response = self.api_client.post("/api/accommodations/", data, format="json")
        self.assertEqual(response.status_code, 403)

    def test_reservation_viewset_create(self):
        """Test creating a reservation via ReservationViewSet."""
        self.api_client.force_authenticate(user=self.user_student)
        data = {
            "accommodation": self.accommodation.id,
            "student_name": "Student One",
            "student_email": "student1@example.com",
            "start_date": date.today().isoformat(),
            "end_date": (date.today() + timedelta(days=10)).isoformat(),
            "status": "pending"
        }
        response = self.api_client.post("/api/reservations/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Reservation.objects.count(), 2)
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(mail.outbox[0].subject.startswith("Reservation Created"))

    def test_reservation_viewset_create_fully_booked(self):
        """Test creating a reservation when accommodation is fully booked."""
        self.accommodation.beds = 1
        self.accommodation.save()
        Reservation.objects.create(
            accommodation=self.accommodation, student_name="Student Two",
            student_email="student2@example.com", start_date=date.today(),
            end_date=date.today() + timedelta(days=10), created_by=self.user_student,
            status="confirmed"
        )
        self.api_client.force_authenticate(user=self.user_student)
        data = {
            "accommodation": self.accommodation.id,
            "student_name": "Student One",
            "student_email": "student1@example.com",
            "start_date": date.today().isoformat(),
            "end_date": (date.today() + timedelta(days=10)).isoformat(),
            "status": "pending"
        }
        response = self.api_client.post("/api/reservations/", data, format="json")
        self.assertEqual(response.status_code, 403)

    def test_rating_viewset_create(self):
        """Test creating a rating via RatingViewSet."""
        self.api_client.force_authenticate(user=self.user_student)
        data = {
            "accommodation": self.accommodation.id,
            "student_name": "Student One",
            "value": 4,
            "comment": "Amazing!"
        }
        response = self.api_client.post("/api/ratings/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.accommodation.refresh_from_db()
        self.assertEqual(self.accommodation.rating, 4)

    # Tests for API Views
    def test_me_view(self):
        """Test MeView returns user information."""
        self.api_client.force_authenticate(user=self.user_student)
        response = self.api_client.get(reverse("me-view"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["university"], "HKU")

    def test_accommodation_filter_view_all_params(self):
        """Test AccommodationFilterView with all query parameters."""
        self.api_client.force_authenticate(user=self.user_student)
        query = (
            "? Inspire_type=AP"
            f"&available_from={date.today().isoformat()}"
            f"&available_to={(date.today() + timedelta(days=20)).isoformat()}"
            "&min_beds=2"
            "&min_bedrooms=1"
            "&min_price=500"
            "&max_price=1500"
            "&campus_label=HKU - Main Campus"
            "&max_distance=1"
        )
        response = self.api_client.get(reverse("accommodation-filter") + query)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_reservation_filter_view(self):
        """Test ReservationFilterView returns user's reservations."""
        self.api_client.force_authenticate(user=self.user_student)
        response = self.api_client.get(reverse("reservation-filter"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_reservation_cancel_view(self):
        """Test ReservationCancelView cancels a reservation."""
        self.api_client.force_authenticate(user=self.user_student)
        response = self.api_client.delete(reverse("reservation-cancel", args=[self.reservation.id]))
        self.assertEqual(response.status_code, 200)
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.status, "cancelled")

    # Tests for Django Views (api/views.py)
    def test_student_accommodation_list(self):
        """Test accommodation list view for students."""
        self.client.force_login(self.user_student)
        with patch("requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: [{"id": self.accommodation.id, "title": "Test Apartment"}]
            )
            response = self.client.get(reverse("accommodation_list"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("accommodations", response.context)
        self.assertEqual(len(response.context["accommodations"]), 1)
        self.assertFalse(response.context["is_cedars"])

    def test_student_accommodation_list_api_error(self):
        """Test accommodation list view handles API errors."""
        self.client.force_login(self.user_student)
        with patch("requests.get") as mock_get:
            mock_get.return_value = MagicMock(status_code=500)
            response = self.client.get(reverse("accommodation_list"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("accommodations", response.context)
        self.assertEqual(len(response.context["accommodations"]), 0)

    def test_accommodation_detail(self):
        """Test accommodation detail view."""
        self.client.force_login(self.user_student)
        with patch("requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: {"id": self.accommodation.id, "title": "Test Apartment"}
            )
            response = self.client.get(reverse("accommodation_detail", args=[self.accommodation.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("accommodation", response.context)
        self.assertEqual(response.context["accommodation"]["id"], self.accommodation.id)

    def test_accommodation_detail_not_found(self):
        """Test accommodation detail view handles not found errors."""
        self.client.force_login(self.user_student)
        with patch("requests.get") as mock_get:
            mock_get.return_value = MagicMock(status_code=404)
            response = self.client.get(reverse("accommodation_detail", args=[999]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("accommodation_list"))

    def test_create_reservation_view_get(self):
        """Test GET request for create reservation view."""
        self.client.force_login(self.user_student)
        with patch("requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: {"id": self.accommodation.id, "title": "Test Apartment"}
            )
            response = self.client.get(reverse("create_reservation") + f"?accommodation={self.accommodation.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)
        self.assertIn("accommodation", response.context)

    def test_create_reservation_view_post(self):
        """Test POST request for create reservation view."""
        self.client.force_login(self.user_student)
        data = {
            "start_date": date.today().isoformat(),
            "end_date": (date.today() + timedelta(days=10)).isoformat()
        }
        with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: {"id": self.accommodation.id, "title": "Test Apartment"}
            )
            mock_post.return_value = MagicMock(status_code=201)
            response = self.client.post(
                reverse("create_reservation") + f"?accommodation={self.accommodation.id}",
                data=data
            )
        self.assertEqual(response.status_code, 200)

    def test_create_reservation_view_post_invalid(self):
        """Test POST request with invalid data for create reservation view."""
        self.client.force_login(self.user_student)
        data = {
            "start_date": (date.today() + timedelta(days=10)).isoformat(),
            "end_date": date.today().isoformat()
        }
        with patch("requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: {"id": self.accommodation.id, "title": "Test Apartment"}
            )
            response = self.client.post(
                reverse("create_reservation") + f"?accommodation={self.accommodation.id}",
                data=data
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)
        self.assertFalse(response.context["form"].is_valid())

    def test_cancel_reservation_view(self):
        """Test cancel reservation view."""
        self.client.force_login(self.user_student)
        with patch("requests.delete") as mock_delete:
            mock_delete.return_value = MagicMock(status_code=204)
            response = self.client.get(reverse("cancel_reservation", args=[self.reservation.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("accommodation_list"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "UniHaven: Reservation Cancelled")

    def test_cancel_reservation_view_error(self):
        """Test cancel reservation view handles errors."""
        self.client.force_login(self.user_student)
        with patch("requests.delete") as mock_delete:
            mock_delete.return_value = MagicMock(status_code=400)
            response = self.client.get(reverse("cancel_reservation", args=[self.reservation.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("accommodation_list"))

    def test_rate_accommodation_view_get(self):
        """Test GET request for rate accommodation view."""
        self.client.force_login(self.user_student)
        with patch("requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: {"id": self.accommodation.id, "title": "Test Apartment"}
            )
            response = self.client.get(reverse("rate_accommodation") + f"?accommodation={self.accommodation.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)
        self.assertIn("accommodation", response.context)

    def test_rate_accommodation_view_post(self):
        """Test POST request for rate accommodation view."""
        self.client.force_login(self.user_student)
        data = {
            "accommodation": self.accommodation.id,
            "value": 5,
            "comment": "Amazing!"
        }
        with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: {"id": self.accommodation.id, "title": "Test Apartment"}
            )
            mock_post.return_value = MagicMock(status_code=201)
            response = self.client.post(reverse("rate_accommodation"), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("accommodation_list"))

    def test_create_accommodation_view_get(self):
        """Test GET request for create accommodation view."""
        self.client.force_login(self.user_staff)
        response = self.client.get(reverse("create_accommodation"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_create_accommodation_view_unauthorized(self):
        """Test unauthorized access to create accommodation view."""
        self.client.force_login(self.user_student)
        response = self.client.get(reverse("create_accommodation"))
        self.assertEqual(response.status_code, 302)

    def test_view_all_reservations(self):
        """Test view all reservations for staff."""
        self.client.force_login(self.user_staff)
        with patch("requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: [{"id": self.reservation.id, "status": "pending"}]
            )
            response = self.client.get(reverse("view_reservations"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("reservations", response.context)
        self.assertEqual(len(response.context["reservations"]), 1)

    def test_cedars_cancel_reservation(self):
        """Test staff cancelling a reservation."""
        self.client.force_login(self.user_staff)
        with patch("requests.delete") as mock_delete:
            mock_delete.return_value = MagicMock(status_code=204)
            response = self.client.get(reverse("cedars_cancel_reservation", args=[self.reservation.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("view_reservations"))

    def test_my_reservations_view(self):
        """Test student's my reservations view."""
        self.client.force_login(self.user_student)
        with patch("requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: [{"id": self.reservation.id, "status": "completed", "end_date": date.today().isoformat()}]
            )
            response = self.client.get(reverse("my_reservations"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("reservations", response.context)
        self.assertTrue(response.context["reservations"][0]["can_rate"])

    def test_view_all_ratings(self):
        """Test view all ratings for staff."""
        self.client.force_login(self.user_staff)
        with patch("requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: [{"id": self.rating.id, "value": 4}]
            )
            response = self.client.get(reverse("view_all_ratings"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("ratings", response.context)
        self.assertEqual(len(response.context["ratings"]), 1)

    # Tests for Users Views
    def test_home_view_authenticated_student(self):
        """Test home view redirects student to student selection."""
        self.client.force_login(self.user_student)
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("student_selection"))

    def test_home_view_authenticated_staff(self):
        """Test home view redirects staff to dashboard."""
        self.client.force_login(self.user_staff)
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("cedars_dashboard"))

    def test_home_view_unauthenticated(self):
        """Test home view redirects unauthenticated user to login."""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login"))

    def test_login_view_get(self):
        """Test GET request for login view."""
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_login_view_post_success(self):
        """Test successful login via POST request."""
        response = self.client.post(reverse("login"), {
            "username": "student1",
            "password": "testpass123"
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("student_selection"))

    def test_logout_view_post(self):
        """Test logout via POST request."""
        self.client.force_login(self.user_student)
        response = self.client.post(reverse("logout"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Logout successful"})

    def test_logout_view_get(self):
        """Test logout via GET request."""
        self.client.force_login(self.user_student)
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))

    def test_student_selection_view(self):
        """Test student selection view for students."""
        self.client.force_login(self.user_student)
        response = self.client.get(reverse("student_selection"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("university", response.context)
        self.assertEqual(response.context["university"], "HKU")

    def test_cedars_dashboard_view(self):
        """Test CEDARS dashboard view for staff."""
        self.client.force_login(self.user_staff)
        response = self.client.get(reverse("cedars_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("university", response.context)
        self.assertEqual(response.context["university"], "HKU")

    # Tests for Admin
    def test_accommodation_admin(self):
        """Test AccommodationAdmin configuration."""
        admin = AccommodationAdmin(Accommodation, AdminSite())
        self.assertEqual(admin.list_display, (
            "title", "property_type", "price", "available_from", "available_to", "is_available", "average_rating"
        ))

    def test_reservation_admin(self):
        """Test ReservationAdmin configuration."""
        admin = ReservationAdmin(Reservation, AdminSite())
        self.assertEqual(admin.list_display, (
            "accommodation", "student_name", "start_date", "end_date", "status", "created_at"
        ))
        self.assertEqual(admin.list_filter, ("status", "start_date", "end_date"))
        self.assertEqual(admin.search_fields, ("accommodation__title", "student_name"))
        self.assertEqual(admin.ordering, ("-created_at",))

    def test_rating_admin(self):
        """Test RatingAdmin configuration."""
        admin = RatingAdmin(Rating, AdminSite())
        self.assertEqual(admin.list_display, (
            "accommodation", "student_name", "value", "created_at"
        ))
        self.assertEqual(admin.list_filter, ("value",))
        self.assertEqual(admin.search_fields, ("accommodation__title", "student_name"))
        self.assertEqual(admin.ordering, ("-created_at",))
