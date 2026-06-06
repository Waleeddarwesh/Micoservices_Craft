from django.core.management.base import BaseCommand
from craft_common.events import EventConsumer
from products.models import Product
from course.models import Course

class Command(BaseCommand):
    help = 'Consume RabbitMQ events for catalog-service'

    def handle(self, *args, **options):
        consumer = EventConsumer(queue_name='catalog_service_queue')
        
        # Subscribe to user.updated to update supplier_name
        consumer.subscribe('user.updated', self.handle_user_updated)
        # Subscribe to review.approved to recalculate rating
        consumer.subscribe('review.approved', self.handle_review_approved)

        self.stdout.write(self.style.SUCCESS('Starting event consumer...'))
        try:
            consumer.start_consuming()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Consumer stopped.'))
            consumer.stop_consuming()

    def handle_user_updated(self, payload):
        user_id = payload.get('user_id')
        updates = payload.get('updates', {})
        first_name = updates.get('first_name')
        last_name = updates.get('last_name')
        if not user_id or (not first_name and not last_name):
            return
            
        supplier_name = f"{first_name} {last_name}".strip()
        
        # Update denormalized supplier_name on Products and Courses
        products_updated = Product.objects.filter(supplier_id=user_id).update(supplier_name=supplier_name)
        courses_updated = Course.objects.filter(supplier_id=user_id).update(supplier_name=supplier_name)
        
        self.stdout.write(f"Updated {products_updated} products and {courses_updated} courses for supplier {user_id}")

    def handle_review_approved(self, payload):
        product_id = payload.get('product_id')
        new_rating = payload.get('new_rating_avg')
        if not product_id or new_rating is None:
            return
            
        Product.objects.filter(ProductID=product_id).update(Rating=new_rating)
        self.stdout.write(f"Updated rating for product {product_id} to {new_rating}")
