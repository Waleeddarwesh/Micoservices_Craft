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
        ]
        read_only_fields = ("VideoNo",)

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
