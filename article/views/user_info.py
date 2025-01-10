from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from article.models.user_info.user_schedule import UserSchedule
from article.models.user_info.user_category import UserCategory
from article.serializers.base_serializers import BaseResponseSerializer
from article.serializers.user_info.user_info_serializers import (
    UserCategoryCreateSerializer,UserScheduleCreateSerializer,UserCategorySerializer,UserScheduleSerializer
)

def handle_error_response(errors, error_code, status_code):
    '''
    #TODO seperate!
    '''
    response_data = {
        "success": False,
        "errorCode": error_code,
        "data": errors
    }
    return Response(BaseResponseSerializer(response_data).data, status=status_code)

class UserCategoryViewSet(viewsets.ViewSet):
    """
    UserCategory 관련 ViewSet입니다.
    """
    queryset = UserCategory.objects.all()
    lookup_field = 'user_email'
    
    @swagger_auto_schema(
        tags=["User Category API"],
        responses={
            200: BaseResponseSerializer,
            400: BaseResponseSerializer,
        },
    )
    def list(self, request, *args, **kwargs):
        """
        모든 UserCategory를 조회합니다.
        """
        queryset = self.queryset
        serializer = UserCategorySerializer(queryset, many=True)
        response_data = {
            "data": serializer.data
        }
        return Response(BaseResponseSerializer(response_data).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
    tags=["User Category API"],
    responses={
        200: BaseResponseSerializer,
        400: BaseResponseSerializer,
        404: BaseResponseSerializer,
    },
    )
    def retrieve(self, request, user_email=None):
        """
        특정 UserCategory를 조회합니다.
        """
        try:
            categories = UserCategory.objects.filter(user_email=user_email)
            if not categories.exists():
                return handle_error_response({"message": "UserCategory not found"}, "ERR404", status.HTTP_404_NOT_FOUND)
            active_categories = categories.filter(is_activated=True)
            category_titles = [category.category.title for category in active_categories]
            response_data = {
                "data": {
                    "userEmail": user_email,
                    "categoryTitles": category_titles
                }
            }
            return Response(BaseResponseSerializer(response_data).data, status=status.HTTP_200_OK)
        except Exception as e:
            return handle_error_response({"message": str(e)}, "ERR500", status.HTTP_500_INTERNAL_SERVER_ERROR)



    @swagger_auto_schema(
    request_body=UserCategoryCreateSerializer,
    responses={
        201: BaseResponseSerializer,
        400: BaseResponseSerializer,
    },
    tags=["User Category API"]
)
    def create(self, request, *args, **kwargs):
        """
        새로운 UserCategory를 생성하거나 업데이트합니다.
        """
        serializer = UserCategoryCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return handle_error_response(serializer.errors, "ERR400", status.HTTP_400_BAD_REQUEST)

        user_email = serializer.validated_data['user_email']
        new_category_ids = serializer.validated_data['categoryIds']
        existing_user_categories = UserCategory.objects.filter(user_email=user_email)
        existing_category_ids = set(existing_user_categories.values_list('category_id', flat=True))
        categories_to_add = set(new_category_ids) - existing_category_ids

        categories_to_deactivate = existing_category_ids - set(new_category_ids)
        UserCategory.objects.filter(user_email=user_email, category_id__in=categories_to_deactivate).update(is_activated=False)
        for category_id in categories_to_add:
            UserCategory.objects.create(user_email=user_email, category_id=category_id, is_activated=True)

        updated_user_categories = UserCategory.objects.filter(user_email=user_email,is_activated=True)
        response_serializer = UserCategorySerializer(updated_user_categories, many=True)
        response_data = {
            "data": response_serializer.data
        }
        return Response(BaseResponseSerializer(response_data).data, status=status.HTTP_201_CREATED)

class UserScheduleViewSet(viewsets.ViewSet):
    """
    UserSchedule 관련 ViewSet입니다.
    """
    queryset = UserSchedule.objects.all()
    lookup_field = 'user_email'
    
    @swagger_auto_schema(
        request_body=UserScheduleCreateSerializer,
        responses={
            201: BaseResponseSerializer,
            400: BaseResponseSerializer,
        },
        tags=["User Schedule API"]
    )
    def create(self, request, *args, **kwargs):
        """
        새로운 User schedule을 생성하거나 기존 데이터를 삭제하고 다시 생성합니다.
        """
        serializer = UserScheduleCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return handle_error_response(serializer.errors, "ERR400", status.HTTP_400_BAD_REQUEST)

        user_email = serializer.validated_data['user_email']
        schedules = serializer.validated_data['schedules']
        UserSchedule.objects.filter(user_email=user_email).delete()
        created_schedules = [
            UserSchedule.objects.create(user_email=user_email, day_of_week=day)
            for day in schedules
        ]

        response_serializer = UserScheduleSerializer(created_schedules, many=True)
        response_data = {
            "data": response_serializer.data
        }
        return Response(BaseResponseSerializer(response_data).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        tags=["User Schedule API"],
        responses={
            200: BaseResponseSerializer,
            400: BaseResponseSerializer,
        },
    )
    def list(self, request, *args, **kwargs):
        """
        모든 User의 Schedule를 조회합니다.
        """
        queryset = self.queryset
        serializer = UserScheduleSerializer(queryset, many=True)
        response_data = {
            "data": serializer.data
        }
        return Response(BaseResponseSerializer(response_data).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["User Schedule API"],
        responses={
            200: BaseResponseSerializer,
            400: BaseResponseSerializer,
            404: BaseResponseSerializer,
        },
    )
    def retrieve(self, request, user_email=None):
        """
        특정 User의 schedule을 조회합니다.
        """
        if not user_email:
            return handle_error_response({"message": "UserSchedule ID is required"}, "ERR400", status.HTTP_400_BAD_REQUEST)

        try:
            schedules = UserSchedule.objects.filter(user_email=user_email)
            if not schedules.exists():
                return handle_error_response({"message": "UserSchedule not found"}, "ERR404", status.HTTP_404_NOT_FOUND)

            schedule_days = [schedule.day_of_week for schedule in schedules]

            response_data = {
                "data": {
                    "user_email": user_email,
                    "schedules": schedule_days
                }
            }
            return Response(BaseResponseSerializer(response_data).data, status=status.HTTP_200_OK)

        except Exception as e:
            return handle_error_response({"message": str(e)}, "ERR500", status.HTTP_500_INTERNAL_SERVER_ERROR)