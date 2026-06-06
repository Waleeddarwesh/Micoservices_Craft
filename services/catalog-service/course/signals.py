from django.db.models.signals import post_save
from django.dispatch import receiver
from craft_common.events import EventPublisher
from pydantic import BaseModel
from .models import Course, Enrollment

publisher = EventPublisher()

# Ad-hoc schemas since craft-common might not have them yet
class CourseCreatedEvent(BaseModel):
    event_type: str = "course.created"
    course_id: int
    title: str
    supplier_id: int

class EnrollmentCreatedEvent(BaseModel):
    event_type: str = "enrollment.created"
    enrollment_id: int
    course_id: int
    user_id: int

@receiver(post_save, sender=Course)
def course_saved(sender, instance, created, **kwargs):
    if created:
        event = CourseCreatedEvent(
            course_id=instance.CourseID,
            title=instance.CourseTitle,
            supplier_id=instance.supplier_id or 0
        )
        publisher.publish(event)

@receiver(post_save, sender=Enrollment)
def enrollment_saved(sender, instance, created, **kwargs):
    if created:
        event = EnrollmentCreatedEvent(
            enrollment_id=instance.EnrollmentID,
            course_id=instance.Course.CourseID,
            user_id=instance.user_id
        )
        publisher.publish(event)