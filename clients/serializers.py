from rest_framework import serializers
from .models import Booking
from clients.models import Room





class BookingSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Booking
        fields = ['id','user', 'room', 'check_in', 'check_out', 'epoca', 'premium', 'preco_total']

