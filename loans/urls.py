from django.urls import path
from .views import check_eligibility, create_loan, view_loan, view_loans_by_customer

urlpatterns = [
    path('check-eligibility/', check_eligibility),
    path('create-loan/', create_loan),
    path('view-loan/<int:loan_id>/', view_loan),
    path('view-loans/<int:customer_id>/', view_loans_by_customer),
]