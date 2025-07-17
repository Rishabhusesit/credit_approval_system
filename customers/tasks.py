import pandas as pd
from celery import shared_task
from .models import Customer
from loans.models import Loan
from datetime import datetime

@shared_task
def ingest_data():
    customer_df = pd.read_excel('customer_data.xlsx')
    loan_df = pd.read_excel('loan_data.xlsx')

    # Normalize column names (remove spaces + lowercase + underscores)
    customer_df.columns = customer_df.columns.str.strip().str.lower().str.replace(' ', '_')
    loan_df.columns = loan_df.columns.str.strip().str.lower().str.replace(' ', '_')

    for _, row in customer_df.iterrows():
        Customer.objects.update_or_create(
            customer_id=row['customer_id'],
            defaults={
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'age': row['age'],
                'phone_number': str(row['phone_number']),
                'monthly_salary': row['monthly_salary'],
                'approved_limit': row['approved_limit'],
                'current_debt': 0.0  # Initial debt
            }
        )

    for _, row in loan_df.iterrows():
        customer = Customer.objects.get(customer_id=row['customer_id'])
        Loan.objects.update_or_create(
            loan_id=row['loan_id'],
            defaults={
                'customer': customer,
                'loan_amount': row['loan_amount'],
                'tenure': row['tenure'],
                'interest_rate': row['interest_rate'],
                'monthly_installment': row['monthly_payment'],
                'emis_paid_on_time': row['emis_paid_on_time'],
                'start_date': pd.to_datetime(row['date_of_approval']).date(),
                'end_date': pd.to_datetime(row['end_date']).date(),
            }
        )
