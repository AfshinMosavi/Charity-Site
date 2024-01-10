from rest_framework import status, generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView
from charities.models import Task
from charities.serializers import (BenefactorSerializer, CharitySerializer, TaskSerializer)
from accounts.permissions import IsBenefactor, IsCharityOwner

class BenefactorRegistration(generics.CreateAPIView):
    serializer_class = BenefactorSerializer
    permission_classes = [IsAuthenticated,]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        response_data = {'detail': 'Registration updated. You are now a benefactor.'}
        return Response(response_data, status=status.HTTP_201_CREATED)

class CharityRegistration(generics.CreateAPIView):
    serializer_class = CharitySerializer
    permission_classes = [IsAuthenticated,]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        response_data = {'detail': 'Registration updated. You have registered your charity.'}
        return Response(response_data, status=status.HTTP_201_CREATED)

class Tasks(generics.ListCreateAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.all_related_tasks_to_user(self.request.user)

    def post(self, request, *args, **kwargs):
        data = {
            **request.data,
            "charity_id": request.user.charity.id
        }
        serializer = self.serializer_class(data = data)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response(serializer.data, status = status.HTTP_201_CREATED)

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            self.permission_classes = [IsAuthenticated, ]
        else:
            self.permission_classes = [IsCharityOwner, ]

        return [permission() for permission in self.permission_classes]

    def filter_queryset(self, queryset):
        filter_lookups = {}
        for name, value in Task.filtering_lookups:
            param = self.request.GET.get(value)
            if param:
                filter_lookups[name] = param
        exclude_lookups = {}
        for name, value in Task.excluding_lookups:
            param = self.request.GET.get(value)
            if param:
                exclude_lookups[name] = param

        return queryset.filter(**filter_lookups).exclude(**exclude_lookups)

class TaskRequest(generics.RetrieveAPIView):
    permission_classes = [IsBenefactor,IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        task_id = self.kwargs.get('task_id')
        try:
            task = Task.objects.get(pk=task_id)
        except  Task.DoesNotExist:
            return Response({'message':'task not found'}, status=status.HTTP_404_NOT_FOUND)   
             
        if task.state != 'P':
            return Response({'detail': 'This task is not pending.'}, status=status.HTTP_404_NOT_FOUND)
            
        task.state = 'W'
        task.assigned_benefactor = request.user.benefactor
        task.save()
        return Response({'detail': 'Request sent.'}, status=status.HTTP_200_OK)

class TaskResponse(generics.CreateAPIView):
    permission_classes = [IsCharityOwner, IsAuthenticated]
    serializer_class = TaskSerializer
    def post(self, request, *args, **kwargs):
        task_id = self.kwargs.get('task_id')
        task = get_object_or_404(Task, pk=task_id)
        response_value = request.data.get('response')
        
        if response_value!= 'A' and response_value != 'R':
            return Response({'detail': 'Required field ("A" for accepted / "R" for rejected)'}, status=status.HTTP_400_BAD_REQUEST)
        if task.state != 'W':
            return Response({'detail': 'This task is not waiting.'}, status=status.HTTP_404_NOT_FOUND)
        if response_value == 'A':
            task.state = 'A'
            task.save()
            return Response({'detail': 'Response sent.'}, status=status.HTTP_200_OK)
        if response_value == 'R':
            task.state = 'P'
            task.assigned_benefactor = None
            task.save()
            return Response({'detail': 'Response sent.'}, status=status.HTTP_200_OK)

class DoneTask(generics.CreateAPIView):
    permission_classes = [IsCharityOwner]
    
    def post(self, request, *args, **kwargs):
        task_id = self.kwargs.get('task_id')
        task = get_object_or_404(Task, pk=task_id)
        if task.state != 'A':
            return Response({'detail': 'Task is not assigned yet.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            task.state = 'D'
            task.save()
            return Response({'detail': 'Task has been done successfully.'}, status=status.HTTP_200_OK)





