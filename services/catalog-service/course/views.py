from django.db.models import F, Max
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache

from rest_framework import generics, permissions, filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.translation import gettext as _

from .models import Course, CourseVideos, Enrollment
from .serializers import (
    CourseSerializer, 
    CourseVideosSerializer, 
    SimpleCoursesSerializer,
    VideoUploadRequestSerializer,
    VideoCompleteUploadSerializer
)
from .services.video_storage_service import VideoStorageService
from .services.video_access_service import VideoAccessService
from .services.video_processing_tasks import process_uploaded_video
from .permissions import IsSupplier


def _get_user_id(request):
    """Safely extract user ID from either StatelessUser or Django User."""
    uid = getattr(request.user, 'id', None)
    return int(uid) if uid is not None else None


def _has_supplier_role(request):
    """Check if the authenticated user has the supplier role in their JWT."""
    payload = getattr(request.user, 'payload', None)
    if payload:
        return 'supplier' in payload.get('roles', [])
    return hasattr(request.user, 'supplier')


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class CoursePermissionMixin:
    def _ensure_course_owner(self, course):
        user_id = _get_user_id(self.request)
        if course.supplier_id != user_id:
            raise PermissionDenied(_("You are not allowed to modify this course."))

    def _ensure_video_owner(self, video):
        user_id = _get_user_id(self.request)
        if video.CourseID.supplier_id != user_id:
            raise PermissionDenied(_("You are not allowed to perform this action on this video."))


class CourseViewSet(viewsets.ModelViewSet, CoursePermissionMixin):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsSupplier]
    filter_backends = [filters.SearchFilter]
    search_fields = ["@CourseTitle", "@Description"]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Course.objects.none()
        user_id = _get_user_id(self.request)
        if not _has_supplier_role(self.request):
            return Course.objects.none()
        return Course.objects.filter(supplier_id=user_id).only(
            "CourseID", "CourseTitle", "Description", "Thumbnail", "supplier_id", "NumberOfUploadedLec"
        )

    # Cache list view for 15 min (public cache)
    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # Cache detail view per-course for 15 min
    @method_decorator(cache_page(60 * 15))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = _get_user_id(request)
        course = serializer.save(supplier_id=user_id)

        return Response(
            CourseSerializer(course).data,
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        self._ensure_course_owner(instance)
        return super().partial_update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        self._ensure_course_owner(instance)
        instance.delete()

    @action(detail=False, methods=["get"], url_path="my-courses")
    def list_own_courses(self, request):
        if not _has_supplier_role(request):
            raise PermissionDenied(_("You are not a supplier."))
        user_id = _get_user_id(request)
        queryset = self.get_queryset().filter(supplier_id=user_id)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class LectureViewSet(viewsets.ModelViewSet, CoursePermissionMixin):
    serializer_class = CourseVideosSerializer
    permission_classes = [IsAuthenticated, IsSupplier]
    lookup_field = "VideoID"
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["@LectureTitle", "@Description"]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return CourseVideos.objects.none()
        user_id = _get_user_id(self.request)
        if not _has_supplier_role(self.request):
            return CourseVideos.objects.none()
        return CourseVideos.objects.select_related(
            "CourseID"
        ).filter(CourseID__supplier_id=user_id).only("VideoID", "LectureTitle", "Description", "CourseID_id")

    def perform_create(self, serializer):
        course = serializer.validated_data["CourseID"]
        user_id = _get_user_id(self.request)

        if course.supplier_id != user_id:
            raise PermissionDenied(_("You are not allowed to create videos for this course."))

        # Use annotation + F to avoid multiple queries
        max_video_no = CourseVideos.objects.filter(CourseID=course).aggregate(Max("VideoNo"))["VideoNo__max"]
        new_video_no = (max_video_no or 0) + 1

        serializer.save(VideoNo=new_video_no)

        # NOTE: NumberOfUploadedLec increment is handled by process_uploaded_video Celery task
        # after confirming the file exists in storage. Not incremented here to avoid double-count.

    def perform_update(self, serializer):
        self._ensure_video_owner(serializer.instance)
        serializer.save()

    def perform_destroy(self, instance):
        self._ensure_video_owner(instance)
        course_id = instance.CourseID_id
        instance.delete()
        Course.objects.filter(pk=course_id).update(
            NumberOfUploadedLec=F("NumberOfUploadedLec") - 1
        )


class SimpleCoursesListAPIView(generics.ListAPIView):
    serializer_class = SimpleCoursesSerializer
    filter_backends = [filters.SearchFilter]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    search_fields = [
        "@CourseTitle",
        "@Description",
    ]

    @method_decorator(cache_page(60 * 15))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Course.objects.only(
            "CourseID", "CourseTitle", "Description", "Thumbnail", "supplier_id"
        )
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return queryset
        # Exclude courses owned by the current supplier
        user_id = _get_user_id(self.request)
        if _has_supplier_role(self.request) and user_id:
            queryset = queryset.exclude(supplier_id=user_id)
        return queryset


class OneCourseDetailAPIView(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    @method_decorator(cache_page(60 * 10))
    def get(self, request, *args, **kwargs):
        course = self.get_object()
        user_id = _get_user_id(request)

        # Cache enrollment check for 10 min (reduces repetitive DB hits)
        cache_key = f"user:{user_id}:enrolled:{course.CourseID}"
        is_enrolled = cache.get(cache_key)
        if is_enrolled is None:
            is_enrolled = Enrollment.objects.filter(
                Course=course, user_id=user_id
            ).exists()
            cache.set(cache_key, is_enrolled, 600)

        is_owner = _has_supplier_role(request) and (course.supplier_id == user_id)

        if not (is_enrolled or is_owner):
            raise PermissionDenied(_("You are not allowed to access this course."))

        return Response(self.get_serializer(course).data)


class CourseLecturesAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(cache_page(60 * 5))
    def get(self, request, pk):
        try:
            course = Course.objects.only("CourseID", "supplier_id").get(pk=pk)
        except Course.DoesNotExist:
            raise NotFound(_("Course not found."))

        user_id = _get_user_id(request)

        # Efficient permission check
        if _has_supplier_role(request) and course.supplier_id == user_id:
            allowed = True
        else:
            allowed = Enrollment.objects.filter(
                Course=course, user_id=user_id
            ).exists()

        if not allowed:
            raise PermissionDenied(
                _("You are not allowed to access lectures for this course.")
            )

        # Optimize lecture query
        lectures = CourseVideos.objects.filter(CourseID=course).only(
            "VideoID", "LectureTitle", "Description", "CourseID_id"
        )

        serializer = CourseVideosSerializer(lectures, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EnrolledCoursesAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CourseSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Course.objects.none()
        user_id = _get_user_id(self.request)
        return Course.objects.filter(
            enrollments__user_id=user_id
        )

    @method_decorator(cache_page(60 * 15))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CreateUploadURLAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSupplier]

    def post(self, request, course_id):
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            raise NotFound(_("Course not found."))

        user_id = _get_user_id(request)
        if course.supplier_id != user_id:
            raise PermissionDenied(_("You are not allowed to add videos to this course."))

        serializer = VideoUploadRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        storage_service = VideoStorageService()
        upload_data = storage_service.generate_upload_url(
            course_id=course_id,
            original_filename=serializer.validated_data['original_filename'],
            content_type=serializer.validated_data['content_type']
        )

        if not upload_data:
            return Response({"detail": _("Failed to generate upload URL.")}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Create the pending video record
        max_video_no = CourseVideos.objects.filter(CourseID=course).aggregate(Max("VideoNo"))["VideoNo__max"]
        new_video_no = (max_video_no or 0) + 1

        video = CourseVideos.objects.create(
            CourseID=course,
            LectureTitle=serializer.validated_data['LectureTitle'],
            Description=serializer.validated_data.get('Description', ''),
            VideoNo=new_video_no,
            original_filename=serializer.validated_data['original_filename'],
            content_type=serializer.validated_data['content_type'],
            file_size=serializer.validated_data['file_size'],
            storage_key=upload_data['storage_key'],
            upload_status='pending'
        )

        return Response({
            "video_id": video.VideoID,
            "upload_url": upload_data['upload_url'],
            "fields": upload_data['fields']
        }, status=status.HTTP_201_CREATED)


class CompleteUploadAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSupplier]

    def post(self, request, video_id):
        try:
            video = CourseVideos.objects.select_related('CourseID').get(pk=video_id)
        except CourseVideos.DoesNotExist:
            raise NotFound(_("Video not found."))

        user_id = _get_user_id(request)
        if video.CourseID.supplier_id != user_id:
            raise PermissionDenied(_("You are not allowed to modify this video."))

        serializer = VideoCompleteUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        video.upload_status = 'uploading' # or processing
        if 'duration' in serializer.validated_data:
            from datetime import timedelta
            video.duration = timedelta(seconds=serializer.validated_data['duration'])
        video.save(update_fields=['upload_status', 'duration'])

        # Trigger Celery task
        process_uploaded_video.delay(video.VideoID)

        return Response({"detail": _("Upload completion registered. Processing started.")})


class VideoPlaybackAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, video_id):
        try:
            video = CourseVideos.objects.select_related('CourseID').get(pk=video_id)
        except CourseVideos.DoesNotExist:
            raise NotFound(_("Video not found."))

        course = video.CourseID
        user_id = _get_user_id(request)
        is_owner = _has_supplier_role(request) and (course.supplier_id == user_id)
        is_enrolled = Enrollment.objects.filter(Course=course, user_id=user_id).exists()
        
        # Or check if user is admin, etc.
        payload = getattr(request.user, 'payload', {}) or {}
        is_admin = 'admin' in payload.get('roles', [])
        if not (is_enrolled or is_owner or is_admin):
            raise PermissionDenied(_("You are not allowed to access this video."))

        if video.upload_status != 'ready':
            return Response({"detail": _("Video is still processing or not ready.")}, status=status.HTTP_400_BAD_REQUEST)

        access_service = VideoAccessService()
        playback_url = access_service.generate_playback_url(video.storage_key)

        if not playback_url:
            return Response({"detail": _("Failed to generate playback URL.")}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "playback_url": playback_url,
            "status": video.upload_status,
            "title": video.LectureTitle,
            "thumbnail": video.thumbnail_url
        })


class VideoWebhookAPIView(APIView):
    permission_classes = [permissions.AllowAny] # Usually validated by signature
    
    def post(self, request):
        """
        Placeholder for external video provider webhooks (e.g., Mux, AWS MediaConvert, Cloudflare Stream).
        """
        # Validate webhook signature here
        
        event_type = request.data.get('type')
        provider_video_id = request.data.get('video_id')
        
        # Idempotent status update logic goes here...
        
        return Response({"status": "received"})
