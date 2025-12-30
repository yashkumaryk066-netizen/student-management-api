from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Book, Member, BookedBook
from .serializers import BookSerializer, MemberSerializer, BookedBookSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status


class BookListCreateView(APIView):
    def get(self, request):
        book = Book.objects.all()
        serializers = BookSerializer(book, many=True)
        return Response(serializers.data)
    
    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
    
class BookRetriView(APIView):
    def get(self, request, id):
        book = Book.objects.get(id=id)
        serializers = BookSerializer(book)
        return Response(serializers.data)
    
    def put(self, request, id):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
    
    def delete(self, request , id):
        book = Book.objects.get(id=id)
        book.delete()
        return Response("deleted")
        
    
class MemberListCreateView(APIView):

    def get(self, request):
        member = Member.objects.all()
        serializers = MemberSerializer(member, many=True)
        return Response(serializers.data)
    
    def post(self, request):
        serializer = MemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
    
class Memberretrive(APIView):
    def get(self, request, id):
        member = Member.objects.get(id=id)
        serializers = MemberSerializer(member)
        return Response(serializers.data)
    
    def put(self, request, id):
        serializer = MemberSerializer.put(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
    
    def delete(self, request, id):
        member = Member.objects.get()
        member.delete()
        return Response("deleted")
        
        
    
class BookedBookListCreateView(APIView):
    def get(self, request):
        bookedbook= BookedBook.objects.all()
        serializers = BookedBookSerializer(bookedbook, many=True)
        return Response(serializers.data)
            
    def post(self, request):
        serializer = BookedBookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)   
                     
class BookedBookRetriveview(APIView):
    def get(self, request, id):
        bookedbook = BookedBook.objects.get(id=id)
        serializers = BookedBookSerializer(bookedbook)
        return Response(serializers.data)
    
    def put(self, request, id):
        serializer = BookedBookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
    
    def delete(self, request, id):
        bookedbook = BookedBook.objects.get(id=id)
        bookedbook.delete()
        return Response("deleted")
        