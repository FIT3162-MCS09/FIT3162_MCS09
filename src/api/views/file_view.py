from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from ..serializers.file_serializer import FileUploadSerializer
from ..serializers import FileSerializer
from ..service.upload_service import UploadService
from models.user import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema,OpenApiParameter

class FileUploadView(APIView):
    @extend_schema(
        request=FileUploadSerializer,
        responses={
            201: FileUploadSerializer,
            400: 'Bad Request'
        }
    )
    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            file = serializer.validated_data['file']
            print(user_id)
            if User.objects.filter(id=user_id).exists() is False:
                return Response({"error": "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)
            success = UploadService.upload_file(file, user_id)
            if success:
                return Response({"message": "File uploaded successfully"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Failed to upload file"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserFilesView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(name='user_id', description='ID of the user', required=True, type=int)
        ],
        responses={
            200: {"type": "object", "properties": {"file_urls": {"type": "array"}}},
            400: 'Bad Request'
        }
    )
    def get(self, request):
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user_id = int(user_id)
        except ValueError:
            return Response({"error": "user_id must be an integer"}, status=status.HTTP_400_BAD_REQUEST)
            
        if not User.objects.filter(id=user_id).exists():
            return Response({"error": "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)
    
        file_urls = UploadService.get_user_files(user_id)
        return Response({"file_urls": file_urls}, status=status.HTTP_200_OK)