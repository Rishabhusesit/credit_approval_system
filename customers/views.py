from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Customer
from .serializers import CustomerSerializer
import math
from django.db import IntegrityError
from django.db.models import Max


@api_view(['POST'])
def register_customer(request):
    data = request.data.copy()
    

    max_id = Customer.objects.aggregate(Max('customer_id'))['customer_id__max'] or 0
    data['customer_id'] = max_id + 1
    monthly_income = int(data['monthly_income'])
    
    
    # Calculate approved limit: round to nearest lakh
    approved_limit = round((36 * monthly_income) / 100000) * 100000
    data['approved_limit'] = approved_limit
    data['monthly_salary'] = monthly_income
    data['current_debt'] = 0.0

    serializer = CustomerSerializer(data=data)
    try:
        if serializer.is_valid():
            serializer.save()
            response = serializer.data
            response['name'] = response['first_name'] + ' ' + response['last_name']
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except IntegrityError:
        return Response(
            {"error": "A customer with this phone number or ID already exists."},
            status=status.HTTP_400_BAD_REQUEST
        )
