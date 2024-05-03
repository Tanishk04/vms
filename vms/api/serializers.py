from rest_framework import serializers
from .models import Vendor, PurchaseOrder

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['id', 'name', 'contact_details', 'address', 'vendor_code', 
                  'on_time_delivery_rate', 'quality_rating_avg', 'average_response_time', 'fulfillment_rate']

    def validate_on_time_delivery_rate(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("On-Time Delivery Rate must be between 0 and 100.")
        return value

    def validate_quality_rating_avg(self, value):
        if value < 0 or value > 10:
            raise serializers.ValidationError("Quality Rating Average must be between 0 and 10.")
        return value

    def validate_average_response_time(self, value):
        if value < 0 or value > float('inf'):
            raise serializers.ValidationError("Average Response Time must be a non-negative number.")
        return value

    def validate_fulfillment_rate(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Fulfillment Rate must be between 0 and 100.")
        return value

class PurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = ['id', 'po_number', 'vendor', 'order_date', 'delivery_date', 
                  'items', 'quantity', 'status', 'quality_rating', 'issue_date', 'acknowledgment_date']
    
    def update(self, instance, validated_data):
        # Check if the acknowledgment_date is present in the request data
        if 'acknowledgment_date' in validated_data:
            # Update the acknowledgment_date field of the instance
            instance.acknowledgment_date = validated_data['acknowledgment_date']
        return instance

class VendorPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['on_time_delivery_rate', 'quality_rating_avg', 'average_response_time', 'fulfillment_rate']
