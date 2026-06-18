from celery import shared_task
from django.utils import timezone
import logging
from course.models import CourseVideos
from course.services.video_storage_service import VideoStorageService

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def process_uploaded_video(self, video_id):
    """
    Celery task to handle post-upload video processing.
    Currently checks if the file exists on S3 and updates status.
    In the future, it can trigger external transcoders or extract thumbnails.
    """
    logger.info(f"Starting processing for video {video_id}")
    try:
        video = CourseVideos.objects.get(VideoID=video_id)
        
        # Avoid processing if not in uploading state (or similar)
        if video.upload_status not in ['uploading', 'pending']:
            logger.warning(f"Video {video_id} is in status {video.upload_status}. Skipping.")
            return
            
        video.upload_status = 'processing'
        video.save(update_fields=['upload_status'])

        # Check file in storage
        storage_service = VideoStorageService()
        if not storage_service.check_file_exists(video.storage_key):
            video.upload_status = 'failed'
            video.processing_error = 'File not found in storage bucket.'
            video.save(update_fields=['upload_status', 'processing_error'])
            return

        # Placeholder for real processing (e.g., getting video duration, generating thumbnail)
        # For now, we just mark it as ready
        video.upload_status = 'ready'
        # Example of getting duration via metadata or webhook later
        # video.duration = ...
        video.save(update_fields=['upload_status'])
        
        # Increment the uploaded lecture count for the course efficiently
        from django.db.models import F
        from course.models import Course
        Course.objects.filter(pk=video.CourseID_id).update(
            NumberOfUploadedLec=F("NumberOfUploadedLec") + 1
        )
        
        logger.info(f"Successfully processed video {video_id} and updated course lecture count")

    except CourseVideos.DoesNotExist:
        logger.error(f"Video {video_id} does not exist.")
    except Exception as exc:
        logger.error(f"Error processing video {video_id}: {exc}")
        try:
            self.retry(exc=exc, countdown=60) # retry after 1 min
        except self.MaxRetriesExceededError:
            # Mark as failed if max retries reached
            CourseVideos.objects.filter(VideoID=video_id).update(
                upload_status='failed', 
                processing_error=str(exc)
            )
