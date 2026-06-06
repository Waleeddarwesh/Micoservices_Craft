from django.db.models.signals import post_save
from django.dispatch import receiver
from craft_common.events import EventPublisher, schemas
from .models import Product

publisher = EventPublisher()

@receiver(post_save, sender=Product)
def product_saved(sender, instance, created, **kwargs):
    if created:
        event = schemas.ProductCreatedEvent(
            product_id=instance.ProductID,
            name=instance.ProductName,
            supplier_id=instance.supplier_id or 0,
            price=float(instance.UnitPrice)
        )
        publisher.publish(event)
    else:
        # Check if stock changed (simplified, normally requires pre_save tracking)
        # We will just publish product updated
        event = schemas.ProductUpdatedEvent(
            product_id=instance.ProductID,
            data={
                "name": instance.ProductName,
                "stock": instance.Stock,
                "price": float(instance.UnitPrice)
            }
        )
        publisher.publish(event)