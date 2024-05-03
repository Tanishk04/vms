from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Vendor, HistoricalPerformance
from django.utils import timezone

@receiver(post_save, sender=Vendor)
def update_historical_performance(sender, instance, created, **kwargs):
    if created:
        # If a new Vendor is created, create a historical performance record
        HistoricalPerformance.objects.create(
            vendor=instance,
            date=timezone.now(),
            on_time_delivery_rate=instance.on_time_delivery_rate,
            quality_rating_avg=instance.quality_rating_avg,
            average_response_time=instance.average_response_time,
            fulfillment_rate=instance.fulfillment_rate
        )
    else:
        # Update the existing historical performance record for the vendor
        try:
            historical_performance = HistoricalPerformance.objects.get(vendor=instance)
        except HistoricalPerformance.DoesNotExist:
            return  # No historical performance record exists for this vendor

        # Update the historical performance metrics
        historical_performance.on_time_delivery_rate = instance.on_time_delivery_rate
        historical_performance.quality_rating_avg = instance.quality_rating_avg
        historical_performance.average_response_time = instance.average_response_time
        historical_performance.fulfillment_rate = instance.fulfillment_rate
        historical_performance.save()


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Count, Avg
from .models import PurchaseOrder, Vendor, HistoricalPerformance
from django.utils import timezone

@receiver(post_save, sender=PurchaseOrder)
def update_performance_metrics(sender, instance, created, **kwargs):
    vendor = instance.vendor

    if created:
        return  # We only update historical performance for existing vendors

    # Get the historical performance record for the vendor if it exists
    try:
        historical_performance = HistoricalPerformance.objects.get(vendor=vendor)
    except HistoricalPerformance.DoesNotExist:
        return  # No historical performance record exists for this vendor

    # Update historical performance metrics based on the latest data
    completed_pos_count = PurchaseOrder.objects.filter(vendor=vendor, status='completed').count()
    on_time_delivery_pos_count = PurchaseOrder.objects.filter(vendor=vendor, status='completed', delivery_date__lte=timezone.now()).count()
    historical_performance.on_time_delivery_rate = (on_time_delivery_pos_count / completed_pos_count) * 100 if completed_pos_count > 0 else 0

    completed_pos_with_quality = PurchaseOrder.objects.filter(vendor=vendor, status='completed', quality_rating__isnull=False)
    historical_performance.quality_rating_avg = completed_pos_with_quality.aggregate(average_quality=Avg('quality_rating'))['average_quality'] or 0

    response_times = PurchaseOrder.objects.filter(vendor=vendor, acknowledgment_date__isnull=False).values_list('issue_date', 'acknowledgment_date')
    total_response_time = sum([(ack_date - issue_date).total_seconds() for issue_date, ack_date in response_times], 0)
    total_acknowledged_pos = len(response_times)
    historical_performance.average_response_time = total_response_time / total_acknowledged_pos if total_acknowledged_pos > 0 else 0

    completed_pos_count = PurchaseOrder.objects.filter(vendor=vendor, status='completed').count()
    historical_performance.fulfillment_rate = (completed_pos_count / vendor.purchaseorder_set.count()) * 100 if vendor.purchaseorder_set.count() > 0 else 0

    # Save the updated historical performance record
    historical_performance.save()
