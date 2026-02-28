from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.http import HttpResponse

from student.models import Payment, ClientSubscription
from student.serializers import PaymentSerializer
from .base import filter_by_owner, get_owner_user

from student.permissions import IsStaffWithPermission

class PaymentListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsStaffWithPermission]
    required_permission = 'fees.view'

    def get(self, request):
        # Optimize with select_related to prevent N+1 queries
        qs = Payment.objects.select_related('student', 'student__parent', 'user').all()

        if request.user.profile.role == 'PARENT':
            qs = qs.filter(student__parent=request.user)
        elif request.user.profile.role == 'STUDENT':
            qs = qs.filter(student__user=request.user)
        else:
            qs = filter_by_owner(qs, request.user)

        return Response(PaymentSerializer(qs, many=True).data)

class PaymentDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        qs = Payment.objects.filter(id=id)
        qs = filter_by_owner(qs, request.user)
        payment = qs.first()

        if not payment:
            return Response({"error": "Payment not found"}, status=404)

        return Response(PaymentSerializer(payment).data)

class InvoiceDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, payment_id):
        try:
            payment = Payment.objects.get(id=payment_id)
            # Security: Allow if superuser or if the payment belongs to the user
            if not request.user.is_superuser and payment.user != request.user:
                return Response({"error": "Permission denied"}, status=403)
            
            sub = ClientSubscription.objects.filter(user=payment.user).first()
            if not sub:
                return Response({"error": "Subscription not found"}, status=404)
                
            from student.services.invoice_service import generate_invoice_pdf
            pdf_buffer = generate_invoice_pdf(payment.user, sub, payment)
            
            response = HttpResponse(pdf_buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="invoice_{payment.id}.pdf"'
            return response
        except Payment.DoesNotExist:
             return Response({"error": "Payment not found"}, status=404)
        except Exception as e:
             return Response({"error": str(e)}, status=500)
