from rest_framework import serializers
from .models import Course, CourseVideos, Enrollment
# from accounts.serializers import CraftersSerializer

class BaseCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "CourseID",
            "Thumbnail",
            "CourseTitle",
            "NumberOfLec",
            "completed",
        ]

class CourseSerializer(BaseCourseSerializer):
    class Meta(BaseCourseSerializer.Meta):
        fields = BaseCourseSerializer.Meta.fields + [
            "CategoryID",
            "Rating",
            "NumberOfRatings",
            "FromDate",
            "ToDate",
            "CourseHours",
            "address",
            "Price",
            "Description",
            "supplier_id",
            "supplier_name",
        ]

class OwnCourseSerializer(BaseCourseSerializer):
    SupplierName = serializers.CharField(
        source="supplier_name", read_only=True
    )

    class Meta(BaseCourseSerializer.Meta):
        fields = BaseCourseSerializer.Meta.fields + [
            "NumberOfUploadedLec",
            "SupplierName",
        ]

class SimpleCoursesSerializer(BaseCourseSerializer):
    class Meta(BaseCourseSerializer.Meta):
        fields = BaseCourseSerializer.Meta.fields + [
            "CategoryID",
            "Rating",
            "NumberOfRatings",
            "FromDate",
            "address",
            "Price",
        ]

class CourseVideosSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseVideos
        fields = [
            "CourseID",
            "VideoID",
            "VideoNo",
            "LectureTitle",
            "Description",
            "VideoFile",
            "original_filename",
            "video_url",
            "thumbnail_url",
            "file_size",
            "content_type",
            "duration",
            "upload_status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "VideoNo",
            "video_url",
            "thumbnail_url",
            "file_size",
            "duration",
            "upload_status",
            "created_at",
            "updated_at",
        )

class VideoUploadRequestSerializer(serializers.Serializer):
    LectureTitle = serializers.CharField(max_length=100)
    Description = serializers.CharField(required=False, allow_blank=True)
    original_filename = serializers.CharField(max_length=255)
    content_type = serializers.CharField(max_length=100)
    file_size = serializers.IntegerField()

class VideoCompleteUploadSerializer(serializers.Serializer):
    # This might include duration or other metadata sent by the frontend
    # after successful S3 upload, if available.
    duration = serializers.IntegerField(required=False, help_text="Duration in seconds, if known")


class EnrollmentSerializer(serializers.ModelSerializer):
    videos = CourseVideosSerializer(
        source="Course.coursevideos_set", many=True, read_only=True
    )

    class Meta:
        model = Enrollment
        fields = [
            "EnrollmentID",
            "Course",
            "user_id",
            "EnrollmentDate",
            "videos",
        ]
