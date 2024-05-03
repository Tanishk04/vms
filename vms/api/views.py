# Import necessary modules
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Vendor, PurchaseOrder
from .serializers import VendorSerializer, PurchaseOrderSerializer, VendorPerformanceSerializer
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import BasicAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Sum
 


# Vendor List and Create View
@authentication_classes([BasicAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
class VendorListCreateAPIView(generics.ListCreateAPIView):
    
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

# Vendor Retrieve, Update, Destroy View
@authentication_classes([BasicAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
class VendorRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [BasicAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

# Purchase Order List and Create View
@authentication_classes([BasicAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
class PurchaseOrderListCreateAPIView(generics.ListCreateAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer

# Purchase Order Retrieve, Update, Destroy View
@authentication_classes([BasicAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
class PurchaseOrderRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer

@authentication_classes([BasicAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
class VendorPerformanceAPIView(generics.RetrieveAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorPerformanceSerializer
    lookup_field = 'pk'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

@authentication_classes([BasicAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
class AcknowledgePurchaseOrderAPIView(APIView):
    def post(self, request, po_id):
        try:
            purchase_order = PurchaseOrder.objects.get(pk=po_id)
        except PurchaseOrder.DoesNotExist:
            return Response({"error": "Purchase Order not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the purchase order has already been acknowledged
        if purchase_order.acknowledgment_date:
            return Response({"error": "Purchase Order already acknowledged"}, status=status.HTTP_400_BAD_REQUEST)

        # Update acknowledgment date
        purchase_order.acknowledgment_date = timezone.now()
        purchase_order.save()

        # Recalculate average response time for the vendor
        vendor = purchase_order.vendor
        response_times = PurchaseOrder.objects.filter(vendor=vendor, acknowledgment_date__isnull=False).values_list('issue_date', 'acknowledgment_date')
        total_response_time = sum([(ack_date - issue_date).total_seconds() for issue_date, ack_date in response_times], 0)
        total_acknowledged_pos = len(response_times)
        vendor.average_response_time = total_response_time / total_acknowledged_pos if total_acknowledged_pos > 0 else 0
        vendor.save()

        return Response({"message": "Purchase Order acknowledged successfully"}, status=status.HTTP_200_OK)


@authentication_classes([BasicAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
class UpdatePurchaseOrderStatusAPIView(APIView):
    def put(self, request, po_id):
        try:
            purchase_order = PurchaseOrder.objects.get(pk=po_id)
        except PurchaseOrder.DoesNotExist:
            return Response({"error": "Purchase Order not found"}, status=status.HTTP_404_NOT_FOUND)
        
        status_data = request.data.get('status')
        rating = request.data.get('rating')

        # Ensure the status_data is in the choices
        if status_data not in [choice[0] for choice in PurchaseOrder.STATUS_CHOICES]:
            return Response({"error": f"Invalid status: {status_data}"}, status=status.HTTP_400_BAD_REQUEST)

        # Update status
        purchase_order.status = status_data
        
        # If the status is completed, update rating and calculate new metrics
        if status_data == 'completed':
            # Check if rating is provided
            if rating is None:
                return Response({"error": "Rating is required for completed orders"}, status=status.HTTP_400_BAD_REQUEST)

            # Update rating for the purchase order
            purchase_order.quality_rating = rating
            purchase_order.save()

            vendor = purchase_order.vendor
            # Check if completion date is before or equal to the delivery date
            if timezone.now() <= purchase_order.delivery_date:
                # If completion date is before or equal to delivery date, increase on_time completed orders count by 1
                vendor.ontime_completed_orders += 1
                vendor.save()
                
            # Update average quality rating in the vendor model
            total_completed_orders = PurchaseOrder.objects.filter(vendor=vendor, status='completed').count()
            total_quality_ratings = PurchaseOrder.objects.filter(vendor=vendor, status='completed').exclude(quality_rating=None).aggregate(total=Sum('quality_rating'))['total']
            vendor.quality_rating_avg = total_quality_ratings / total_completed_orders if total_completed_orders > 0 else 0
            vendor.save()
            
            # Get the total completed orders for the vendor
            total_completed_orders = PurchaseOrder.objects.filter(vendor=vendor, status='completed').count()
            # Get the count of completed orders that were delivered on time
            on_time_delivered_orders = vendor.ontime_completed_orders
            # Calculate the on-time delivery rate as a percentage
            on_time_delivery_rate = (on_time_delivered_orders / total_completed_orders) * 100 if total_completed_orders > 0 else 0
            vendor.on_time_delivery_rate = on_time_delivery_rate
            vendor.save()


            # Calculate new fulfillment rate
            total_orders = PurchaseOrder.objects.filter(vendor=vendor).count()
            completed_orders = PurchaseOrder.objects.filter(vendor=vendor, status='completed').count()
            fulfillment_rate = (completed_orders / total_orders) * 100 if total_orders > 0 else 0
            vendor.fulfillment_rate = fulfillment_rate
            vendor.save()

        # Save the updated purchase order
        purchase_order.save()

        # Serialize and return updated purchase order
        serializer = PurchaseOrderSerializer(purchase_order)
        return Response(serializer.data, status=status.HTTP_200_OK)
