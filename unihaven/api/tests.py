from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from api.models import Accommodation, Reservation
from django.core import mail
from datetime import date, timedelta
import requests
from unittest.mock import patch
import json

User = get_user_model()

class APITestCaseBase(APITestCase):
    def setUp(self):
        self.client = APIClient()
    
        self.users = {
            'hku_staff': {'username': 'hkustaff1', 'password': 'staf1234'},
            'hkust_staff': {'username': 'hkuststaff1', 'password': 'staf1234'},
            'hku_student1': {'username': 'hku1', 'password': 'student123'},
            'hku_student2': {'username': 'hku2', 'password': 'student123'},
            'hkust_student': {'username': 'hkust1', 'password': 'student123'},
            'cuhk_student': {'username': 'cuhkstud1', 'password': 'student123'},
        }
        
        self.hku_staff = User.objects.create_user(
            username='hkustaff1',
            password='staf1234',
            email='hkustaff1@unihaven.hk',
            is_cedars_staff=True,
            university='HKU'
        )
        
        self.hkust_staff = User.objects.create_user(
            username='hkuststaff1',
            password='staf1234',
            email='hkuststaff1@unihaven.hk',
            is_cedars_staff=True,
            university='HKUST'
        )
        
        self.hku_student1 = User.objects.create_user(
            username='hku1',
            password='student123',
            email='hku1@unihaven.hk',
            is_student=True,
            university='HKU'
        )
        
        self.hku_student2 = User.objects.create_user(
            username='hku2',
            password='student123',
            email='hku2@unihaven.hk',
            is_student=True,
            university='HKU'
        )
        
        self.hkust_student = User.objects.create_user(
            username='hkust1',
            password='student123',
            email='hkust1@unihaven.hk',
            is_student=True,
            university='HKUST'
        )
        
        self.cuhk_student = User.objects.create_user(
            username='cuhkstud1',
            password='student123',
            email='cuhkstud1@unihaven.hk',
            is_student=True,
            university='CUHK'
        )
        
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                'SuggestedAddress': [{
                    'Address': {
                        'PremisesAddress': {
                            'GeospatialInformation': {
                                'Latitude': '22.283',
                                'Longitude': '114.137'
                            },
                            'GeoAddress': 'TEST_GEO_ADDRESS'
                        }
                    }
                }]
            }
            self.accommodation = Accommodation.objects.create(
                title='Test HKU Accommodation',
                description='A test accommodation for HKU students',
                property_type='AP',
                price=1000.00,
                beds=2,
                bedrooms=1,
                address='123 HKU Street',
                flat_number='1A',
                floor_number='1',
                room_number='101',
                available_from=date.today(),
                available_to=date.today() + timedelta(days=365),
                is_available=True,
                universities_offered=['HKU'],
                created_by=self.hku_staff
            )

    def get_token(self, username, password):
        login_url = reverse('login')
        response = self.client.post(login_url, {'username': username, 'password': password}, format='multipart')
        self.assertEqual(response.status_code, 302)  
        me_url = reverse('me-view')
        response = self.client.get(me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data['token']

    def authenticate(self, user_key):
        username = self.users[user_key]['username']
        password = self.users[user_key]['password']
        token = self.get_token(username, password)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

class AccommodationViewSetTests(APITestCaseBase):
    @patch('requests.get')
    def test_list_accommodations_hku_student(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'SuggestedAddress': [{
                'Address': {
                    'PremisesAddress': {
                        'GeospatialInformation': {
                            'Latitude': '22.283',
                            'Longitude': '114.137'
                        },
                        'GeoAddress': 'TEST_GEO_ADDRESS'
                    }
                }
            }]
        }
        self.authenticate('hku_student1')
        url = reverse('accommodation-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test HKU Accommodation')

    @patch('requests.get')
    def test_create_accommodation_hku_staff(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'SuggestedAddress': [{
                'Address': {
                    'PremisesAddress': {
                        'GeospatialInformation': {
                            'Latitude': '22.284',
                            'Longitude': '114.138'
                        },
                        'GeoAddress': 'NEW_GEO_ADDRESS'
                    }
                }
            }]
        }
        self.authenticate('hku_staff')
        url = reverse('accommodation-list')
        data = {
            'title': 'New HKU Accommodation',
            'description': 'A new accommodation for HKU students',
            'property_type': 'AP',
            'price': 1500.00,
            'beds': 1,
            'bedrooms': 1,
            'address': '456 HKU Street',
            'flat_number': '2B',
            'floor_number': '2',
            'room_number': '202',
            'available_from': str(date.today()),
            'available_to': str(date.today() + timedelta(days=365)),
            'is_available': True,
            'universities_offered': ['HKU']
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Accommodation.objects.count(), 2)
        self.assertEqual(response.data['title'], 'New HKU Accommodation')

    @patch('requests.get')
    def test_create_accommodation_student_denied(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'SuggestedAddress': [{
                'Address': {
                    'PremisesAddress': {
                        'GeospatialInformation': {
                            'Latitude': '22.285',
                            'Longitude': '114.139'
                        },
                        'GeoAddress': 'INVALID_GEO_ADDRESS'
                    }
                }
            }]
        }
        self.authenticate('hku_student1')
        url = reverse('accommodation-list')
        data = {
            'title': 'Invalid Accommodation',
            'description': 'Invalid accommodation by student',
            'property_type': 'AP',
            'price': 2000.00,
            'beds': 1,
            'bedrooms': 1,
            'address': '789 Invalid Street',
            'flat_number': '3C',
            'floor_number': '3',
            'room_number': '303',
            'available_from': str(date.today()),
            'available_to': str(date.today() + timedelta(days=365)),
            'is_available': True,
            'universities_offered': ['HKU']
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Accommodation.objects.count(), 1)

    @patch('requests.get')
    def test_update_accommodation_hku_staff(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'SuggestedAddress': [{
                'Address': {
                    'PremisesAddress': {
                        'GeospatialInformation': {
                            'Latitude': '22.283',
                            'Longitude': '114.137'
                        },
                        'GeoAddress': 'TEST_GEO_ADDRESS'
                    }
                }
            }]
        }
        self.assertTrue(Accommodation.objects.filter(id=self.accommodation.id).exists())
        self.authenticate('hku_staff')
        url = reverse('accommodation-detail', args=[self.accommodation.id])
        data = {'title': 'Updated HKU Accommodation'}
        response = self.client.patch(url, data, format='json')
        if response.status_code != status.HTTP_200_OK:
            print(f"Update response: {response.status_code}, {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.accommodation.refresh_from_db()
        self.assertEqual(self.accommodation.title, 'Updated HKU Accommodation')

    @patch('requests.get')
    def test_delete_accommodation_hku_staff(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'SuggestedAddress': [{
                'Address': {
                    'PremisesAddress': {
                        'GeospatialInformation': {
                            'Latitude': '22.283',
                            'Longitude': '114.137'
                        },
                        'GeoAddress': 'TEST_GEO_ADDRESS'
                    }
                }
            }]
        }
        self.assertTrue(Accommodation.objects.filter(id=self.accommodation.id).exists())
        self.authenticate('hku_staff')
        url = reverse('accommodation-detail', args=[self.accommodation.id])
        response = self.client.delete(url)
        if response.status_code != status.HTTP_204_NO_CONTENT:
            print(f"Delete response: {response.status_code}, {response.data}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Accommodation.objects.count(), 0)

class ReservationViewSetTests(APITestCaseBase):
    def test_create_reservation_hku_student(self):
        self.authenticate('hku_student1')
        url = reverse('reservation-list')
        data = {
            'accommodation': self.accommodation.id,
            'start_date': str(date.today()),
            'end_date': str(date.today() + timedelta(days=30))
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reservation.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Reservation Made Notification', mail.outbox[0].subject)

    def test_create_reservation_cuhk_student_denied(self):
        self.authenticate('cuhk_student')
        url = reverse('reservation-list')
        data = {
            'accommodation': self.accommodation.id,
            'start_date': str(date.today()),
            'end_date': str(date.today() + timedelta(days=30))
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Reservation.objects.count(), 0)

    def test_cancel_reservation_hku_student(self):
        reservation = Reservation.objects.create(
            student=self.hku_student1,
            accommodation=self.accommodation,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            status='pending'
        )
        self.authenticate('hku_student1')
        url = reverse('reservation-detail', args=[reservation.id])
        response = self.client.delete(url)
        reservation.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(reservation.status, 'cancelled')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Reservation Cancelled Notification', mail.outbox[0].subject)

    def test_list_reservations_hku_staff(self):
        Reservation.objects.create(
            student=self.hku_student1,
            accommodation=self.accommodation,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            status='pending'
        )
        self.authenticate('hku_staff')
        url = reverse('reservation-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class AccommodationFilterViewTests(APITestCaseBase):
    def test_filter_accommodations_hku_student(self):
        self.authenticate('hku_student1')
        url = reverse('accommodation-filter')
        params = {
            'property_type': 'AP',
            'min_beds': 1,
            'max_price': 2000.00,
            'latitude': 22.283,
            'longitude': 114.137,
        }
        response = self.client.get(url, params)
        if len(response.data) != 1:
            print(f"Filter response: {response.status_code}, {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test HKU Accommodation')

class ReservationFilterViewTests(APITestCaseBase):
    def test_filter_reservations_hku_student(self):
        Reservation.objects.create(
            student=self.hku_student1,
            accommodation=self.accommodation,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            status='pending'
        )
        self.authenticate('hku_student1')
        url = reverse('reservation-filter')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class ReservationCancelViewTests(APITestCaseBase):
    def test_cancel_reservation_hku_student(self):
        reservation = Reservation.objects.create(
            student=self.hku_student1,
            accommodation=self.accommodation,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            status='pending'
        )
        self.authenticate('hku_student1')
        url = reverse('reservation-cancel', args=[reservation.id])
        response = self.client.delete(url)
        reservation.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(reservation.status, 'cancelled')

class MeViewTests(APITestCaseBase):
    def test_me_view_hku_student(self):
        self.authenticate('hku_student1')
        url = reverse('me-view')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'hku1')
        self.assertEqual(response.data['role'], 'student')
