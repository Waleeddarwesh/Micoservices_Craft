from django.db import models
from products.models import Category
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.signals import pre_save
from django.dispatch import receiver
from craft_common.utils.translation import translate_text

class Course(models.Model):
    CourseID = models.AutoField(primary_key=True)
    Thumbnail = models.ImageField(upload_to='course_thumbnails/%Y/%m/%d', blank=True, null=True)
    CourseTitle = models.CharField(max_length=100)
    CategoryID = models.ForeignKey(Category, on_delete=models.CASCADE)
    Rating =  models.DecimalField(max_digits=10, decimal_places=2,default= 5.0,validators=(MinValueValidator(0.0), MaxValueValidator(5.0))) 
    completed = models.BooleanField(default=False)
    NumberOfRatings = models.IntegerField(default=0)
    FromDate = models.DateTimeField(blank=True, null=True)
    ToDate = models.DateTimeField(blank=True, null=True)
    CourseHours = models.IntegerField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    NumberOfLec = models.IntegerField(default=0,blank=True, null=True)
    NumberOfUploadedLec = models.IntegerField(default=0,blank=True, null=True)
    Price = models.DecimalField(max_digits=10, decimal_places=2)
    Description = models.TextField()
    supplier_id = models.BigIntegerField(null=True, blank=True)
    supplier_name = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return f"{self.CourseTitle}"

    def update_rating(self, new_rating: float):
        self.Rating = new_rating
        self.save(update_fields=['Rating'])
    
class CourseVideos(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('uploading', 'Uploading'),
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('failed', 'Failed'),
    )

    VideoID = models.AutoField(primary_key=True)
    CourseID = models.ForeignKey(Course, on_delete=models.CASCADE)
    LectureTitle = models.CharField(max_length=100)
    VideoNo = models.IntegerField()
    Description = models.TextField()
    
    # Legacy direct upload field (kept for backward compatibility, made optional)
    VideoFile = models.FileField(upload_to='videos/%y/%m/%d', null=True, blank=True)
    
    # Cloud storage fields
    original_filename = models.CharField(max_length=255, null=True, blank=True)
    storage_key = models.CharField(max_length=512, null=True, blank=True)
    video_url = models.URLField(max_length=1024, null=True, blank=True)
    thumbnail_url = models.URLField(max_length=1024, null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    content_type = models.CharField(max_length=100, null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    
    # Upload tracking
    upload_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processing_error = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['CourseID', 'VideoNo'], name='unique_lecture_per_course')
        ]

    def __str__(self):
        return f"{self.LectureTitle}"

class Enrollment(models.Model):
    EnrollmentID = models.AutoField(primary_key=True)
    Course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    user_id = models.BigIntegerField(default=1)
    EnrollmentDate = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['Course', 'user_id'], name='unique_enrollment')
        ]

    def __str__(self):
        return f"Enrollment ID: {self.EnrollmentID}, Course: {self.Course.CourseTitle}"

@receiver(pre_save, sender=Course)
def auto_translate_course(sender, instance, **kwargs):
    if not instance.CourseTitle_ar and instance.CourseTitle_en:
        instance.CourseTitle_ar = translate_text(instance.CourseTitle_en, source='en', target='ar')
    elif not instance.CourseTitle_en and instance.CourseTitle_ar:
        instance.CourseTitle_en = translate_text(instance.CourseTitle_ar, source='ar', target='en')

    if not instance.Description_ar and instance.Description_en:
        instance.Description_ar = translate_text(instance.Description_en, source='en', target='ar')
    elif not instance.Description_en and instance.Description_ar:
        instance.Description_en = translate_text(instance.Description_ar, source='ar', target='en')

    if not instance.address_ar and instance.address_en:
        instance.address_ar = translate_text(instance.address_en, source='en', target='ar')
    elif not instance.address_en and instance.address_ar:
        instance.address_en = translate_text(instance.address_ar, source='ar', target='en')

@receiver(pre_save, sender=CourseVideos)
def auto_translate_coursevideo(sender, instance, **kwargs):
    if not instance.LectureTitle_ar and instance.LectureTitle_en:
        instance.LectureTitle_ar = translate_text(instance.LectureTitle_en, source='en', target='ar')
    elif not instance.LectureTitle_en and instance.LectureTitle_ar:
        instance.LectureTitle_en = translate_text(instance.LectureTitle_ar, source='ar', target='en')

    if not instance.Description_ar and instance.Description_en:
        instance.Description_ar = translate_text(instance.Description_en, source='en', target='ar')
    elif not instance.Description_en and instance.Description_ar:
        instance.Description_en = translate_text(instance.Description_ar, source='ar', target='en')