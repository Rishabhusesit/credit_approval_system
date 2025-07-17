from rest_framework import serializers
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        extra_kwargs = {
            'customer_id': {'required': False},
            'current_debt': {'required': False, 'default': 0.0}
        }
