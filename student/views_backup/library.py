from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated

from student.models import LibraryBook, BookIssue
from student.serializers import LibraryBookSerializer, BookIssueSerializer
from student.permissions import IsTeacherOrAdmin
from .base import filter_by_owner, get_owner_user

class LibraryBookListCreateView(generics.ListCreateAPIView):
    queryset = LibraryBook.objects.all()
    serializer_class = LibraryBookSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class LibraryBookDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LibraryBook.objects.all()
    serializer_class = LibraryBookSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

class BookIssueListCreateView(generics.ListCreateAPIView):
    queryset = BookIssue.objects.all()
    serializer_class = BookIssueSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(
            self.queryset.select_related('book', 'student'), 
            self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))
