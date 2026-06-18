import boto3
from botocore.exceptions import ClientError
from django.conf import settings
import uuid
import logging

logger = logging.getLogger(__name__)

class VideoStorageService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL
        )
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    def generate_upload_url(self, course_id, original_filename, content_type):
        """
        Generate a presigned URL to upload a video file to S3.
        """
        # Generate a unique storage key
        extension = original_filename.split('.')[-1] if '.' in original_filename else 'mp4'
        unique_id = str(uuid.uuid4())
        storage_key = f"courses/{course_id}/videos/{unique_id}.{extension}"
        
        try:
            response = self.s3_client.generate_presigned_post(
                self.bucket_name,
                storage_key,
                Fields={
                    "Content-Type": content_type
                },
                Conditions=[
                    {"Content-Type": content_type},
                    ["content-length-range", 0, settings.MAX_VIDEO_SIZE_MB * 1024 * 1024]
                ],
                ExpiresIn=settings.VIDEO_UPLOAD_EXPIRATION
            )
            return {
                "upload_url": response["url"],
                "fields": response["fields"],
                "storage_key": storage_key
            }
        except ClientError as e:
            logger.error(f"Error generating presigned upload URL: {e}")
            return None

    def check_file_exists(self, storage_key):
        """
        Check if the uploaded file exists in the S3 bucket.
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=storage_key)
            return True
        except ClientError:
            return False
