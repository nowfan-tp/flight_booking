from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .models import Flight, Ticket
from .serializers import FlightSerializer, TicketSerializer
from datetime import datetime

from rest_framework.authentication import TokenAuthentication


class FlightCreateView(generics.CreateAPIView):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

class FlightSearchView(APIView):
    def post(self, request, *args, **kwargs):
        print("Received request data:", request.data)  # Debugging line
        departure_city = request.data.get('departure_city')
        destination_city = request.data.get('destination_city')
        departure_time = request.data.get('departure_time')
        
        # Start with all flights
        queryset = Flight.objects.all()

        # Apply filters if provided
        if departure_city:
            queryset = queryset.filter(departure_city=departure_city)
        if destination_city:
            queryset = queryset.filter(destination_city=destination_city)
        
        if departure_time:
            try:
                # Convert the incoming departure_time string to a datetime object
                departure_time_dt = datetime.strptime(departure_time, "%Y-%m-%d %H:%M:%S")
                # Format it back to ISO 8601
                departure_time_iso = departure_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                
                queryset = queryset.filter(departure_time=departure_time_iso)  # Filter using ISO formatted datetime
            except ValueError:
                return Response({"error": "Invalid departure_time format."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if any flights match the filters
        if queryset.exists():
            serializer = FlightSerializer(queryset, many=True)  # Serialize multiple instances
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "No flights found matching the criteria."}, status=status.HTTP_404_NOT_FOUND)
        


class BookFlightView(APIView):
    def post(self, request, flight_id, *args, **kwargs):
        try:
            flight = Flight.objects.get(id=flight_id)
        except Flight.DoesNotExist:
            return Response({"error": "Flight not found."}, status=status.HTTP_404_NOT_FOUND)

        seat_number = request.data.get('seat_number')
        user = request.user
        # Create a booking
        ticket = Ticket.objects.create(
            user=user,
            flight=flight,
            seat_number=seat_number,
            booking_status='confirmed'
        )

        flight.save()

        # Serialize the booking data to return
        serializer = TicketSerializer(ticket)
        return Response(serializer.data, status=status.HTTP_201_CREATED)