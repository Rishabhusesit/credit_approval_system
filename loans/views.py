from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Loan
from customers.models import Customer
from .serializers import LoanSerializer
from datetime import datetime


def calculate_monthly_installment(principal, rate, tenure):
    r = rate / (12 * 100)
    emi = principal * r * ((1 + r)**tenure) / ((1 + r)**tenure - 1)
    return round(emi, 2)


#  REUSABLE HELPER FUNCTION
def evaluate_eligibility(customer, loan_amount, interest_rate, tenure):
    loans = Loan.objects.filter(customer=customer)
    score = 0

    total_emis = sum(loan.tenure for loan in loans)
    total_paid = sum(loan.emis_paid_on_time for loan in loans)
    if total_emis:
        score += min((total_paid / total_emis) * 30, 30)

    score += min(len(loans) * 2, 20)

    current_year = datetime.now().year
    recent_loans = [l for l in loans if l.start_date.year == current_year]
    score += min(len(recent_loans) * 5, 20)

    total_volume = sum(loan.loan_amount for loan in loans)
    score += min((total_volume / 1000000) * 5, 20)

    if customer.current_debt > customer.approved_limit:
        score = 0

    credit_score = round(min(score, 100))
    requested_emi = calculate_monthly_installment(loan_amount, interest_rate, tenure)
    total_existing_emi = sum(loan.monthly_installment for loan in loans)
    salary_threshold = 0.5 * customer.monthly_salary

    approve = False
    corrected_interest = interest_rate

    if total_existing_emi + requested_emi > salary_threshold:
        approve = False
    elif credit_score > 50:
        approve = True
    elif 30 < credit_score <= 50:
        approve = True
        if corrected_interest < 12:
            corrected_interest = 12
    elif 10 < credit_score <= 30:
        approve = True
        if corrected_interest < 16:
            corrected_interest = 16

    return {
        'approval': approve,
        'corrected_interest_rate': corrected_interest,
        'monthly_installment': requested_emi,
        'credit_score': credit_score
    }


# /check-eligibility
@api_view(['POST'])
def check_eligibility(request):
    data = request.data
    try:
        customer = Customer.objects.get(customer_id=data['customer_id'])
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

    result = evaluate_eligibility(
        customer,
        float(data['loan_amount']),
        float(data['interest_rate']),
        int(data['tenure'])
    )

    return Response({
        'customer_id': customer.customer_id,
        'approval': result['approval'],
        'interest_rate': float(data['interest_rate']),
        'corrected_interest_rate': result['corrected_interest_rate'],
        'tenure': int(data['tenure']),
        'monthly_installment': result['monthly_installment']
    }, status=status.HTTP_200_OK)


#  /create-loan
@api_view(['POST'])
def create_loan(request):
    data = request.data
    try:
        customer = Customer.objects.get(customer_id=data['customer_id'])
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

    result = evaluate_eligibility(
        customer,
        float(data['loan_amount']),
        float(data['interest_rate']),
        int(data['tenure'])
    )

    if not result['approval']:
        return Response({
            'loan_id': None,
            'customer_id': data['customer_id'],
            'loan_approved': False,
            'message': 'Loan not approved based on eligibility',
            'monthly_installment': result['monthly_installment']
        }, status=status.HTTP_200_OK)

    loan = Loan.objects.create(
        customer=customer,
        loan_id=Loan.objects.count() + 1,
        loan_amount=float(data['loan_amount']),
        tenure=int(data['tenure']),
        interest_rate=float(result['corrected_interest_rate']),
        monthly_installment=result['monthly_installment'],
        emis_paid_on_time=0,
        start_date=datetime.today().date(),
        end_date=datetime.today().date().replace(year=datetime.today().year + int(data['tenure'] // 12))
    )

    customer.current_debt += float(data['loan_amount'])
    customer.save()

    return Response({
        'loan_id': loan.loan_id,
        'customer_id': customer.customer_id,
        'loan_approved': True,
        'message': 'Loan approved and created successfully',
        'monthly_installment': loan.monthly_installment
    }, status=status.HTTP_201_CREATED)


# /view-loan/<loan_id>
@api_view(['GET'])
def view_loan(request, loan_id):
    try:
        loan = Loan.objects.get(loan_id=loan_id)
        customer = loan.customer
    except Loan.DoesNotExist:
        return Response({'error': 'Loan not found'}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'loan_id': loan.loan_id,
        'customer': {
            'id': customer.customer_id,
            'first_name': customer.first_name,
            'last_name': customer.last_name,
            'phone_number': customer.phone_number,
            'age': customer.age
        },
        'loan_amount': loan.loan_amount,
        'interest_rate': loan.interest_rate,
        'monthly_installment': loan.monthly_installment,
        'tenure': loan.tenure
    }, status=status.HTTP_200_OK)


# /view-loans/<customer_id>
@api_view(['GET'])
def view_loans_by_customer(request, customer_id):
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

    loans = Loan.objects.filter(customer=customer)
    loan_data = []
    for loan in loans:
        repayments_left = loan.tenure - loan.emis_paid_on_time
        loan_data.append({
            'loan_id': loan.loan_id,
            'loan_amount': loan.loan_amount,
            'interest_rate': loan.interest_rate,
            'monthly_installment': loan.monthly_installment,
            'repayments_left': repayments_left
        })
    return Response(loan_data, status=status.HTTP_200_OK)
