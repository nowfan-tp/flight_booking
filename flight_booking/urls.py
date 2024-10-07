from django.urls import path
from .views import FlightSearchView, BookFlightView

urlpatterns = [
    path('flights/search/', FlightSearchView.as_view(), name='flight-search'),
    path('flights/<int:flight_id>/book/', BookFlightView.as_view(), name='flight-book'),
]

