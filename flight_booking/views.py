from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .models import Flight, Ticket
from .serializers import FlightSerializer, TicketSerializer
from rest_framework.authentication import TokenAuthentication

class FlightSearchView(generics.ListAPIView):
    serializer_class = FlightSerializer

    def get_queryset(self):
        departure_city = self.request.query_params.get('departure_city')
        destination_city = self.request.query_params.get('destination_city')
        departure_time = self.request.query_params.get('departure_time')
        queryset = Flight.objects.all()

        try:
            if departure_city and destination_city and departure_time:
                queryset = queryset.filter(
                    Q(departure_city=departure_city) & 
                    Q(destination_city=destination_city) & 
                    Q(departure_time__date=departure_time)
                )
        except Exception as e:
            print(f"Error occurred: {e}")  # Print error to console for debugging
            return queryset  # Or raise an exception or return an error response
        
        return queryset

class BookFlightView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, flight_id):
        try:
            flight = Flight.objects.get(id=flight_id)
        except Flight.DoesNotExist:
            return Response({'error': 'Flight not found'}, status=status.HTTP_404_NOT_FOUND)

        seat_number = request.data.get('seat_number')

        # Check if the seat is already booked
        if Ticket.objects.filter(flight=flight, seat_number=seat_number).exists():
            return Response({'error': 'Seat already booked'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a ticket for the authenticated user
        ticket = Ticket.objects.create(
            user=request.user,
            flight=flight,
            seat_number=seat_number,
            booking_status='confirmed'
        )

        return Response({'message': 'Flight booked successfully', 'ticket_id': ticket.id}, status=status.HTTP_201_CREATED)

