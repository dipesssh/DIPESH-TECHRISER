from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
# Serializer to convert Blog model to/from JSON
from .serializers import BlogSerializers, CommentSerializer
from rest_framework import status

# Permissions and authentication for secure API
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication # type: ignore

from .models import Blog, Comment
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage


#  Public blog view – accessible without login

class PublicBlogView(APIView):
    authentication_classes = []  # 👈 Must be empty
    permission_classes = []      # 👈 Must be empty

    def get(self, request):
        try:
            blogs = Blog.objects.all().order_by('?')

            if request.GET.get('search'):
                search = request.GET.get('search')
                blogs = blogs.filter(Q(title__icontains=search) | Q(blog_text__icontains=search))


            page_number =request.GET.get('page',1)
            paginator = Paginator(blogs,5)

            serializer = BlogSerializers(paginator.page(page_number), many=True)

            return Response({
                'data': serializer.data,
                'message': "Public blogs fetched successfully"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({
                'data': {},
                'message': 'Something went wrong or invalid page'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# 🔐 Private blog view – requires login & JWT token

class BlogView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        try:
            # Get all blogs for current user
            blogs = Blog.objects.filter(user=request.user).order_by('-created_at')  # Newest first
            
            # Search functionality
            if search_query := request.GET.get('search'):
                blogs = blogs.filter(
                    Q(title__icontains=search_query) | 
                    Q(blog_text__icontains=search_query)
                )
            
            # Pagination (5 posts per page)
            paginator = Paginator(blogs, 5)
            page_number = request.GET.get('page', 1)
            
            try:
                current_page = paginator.page(page_number)
            except EmptyPage:
                return Response(
                    {"data": [], "message": "Page not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = BlogSerializers(current_page, many=True)
            
            return Response({
                "data": serializer.data,
                "pagination": {
                    "total_pages": paginator.num_pages,
                    "current_page": current_page.number,
                    "has_next": current_page.has_next(),
                    "has_previous": current_page.has_previous(),
                    "total_items": paginator.count
                },
                "message": "Blogs fetched successfully"
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error: {str(e)}")  # Better error logging
            return Response(
                {"data": {}, "message": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


     # POST: Create a new blog
    def post(self, request):
        try:
            data = request.data
            data['user'] = request.user.id
            serializer = BlogSerializers(data = data)

            if not serializer.is_valid():
                return Response({
                    'data': serializer.errors,
                    'message':'something went wrong'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()

            return Response({
                'data': serializer.data,
                'message': "blog created successfully"
            }, status=status.HTTP_201_CREATED)


        except Exception as e:
            print(e)

            return Response({
                    'data': {},
                    'message':'something went wrong'
                }, status=status.HTTP_400_BAD_REQUEST)
        
    # PATCH: Update an existing blog
        
    def patch(self, request):
        try:
            data = request.data
            blog = Blog.objects.filter(uid=data.get('uid')).first()  # ✅ FIXED

            if not blog:
                return Response({
                    'data': {},
                    'message': 'Invalid blog UID'
                }, status=status.HTTP_400_BAD_REQUEST)

            if request.user != blog.user:  # ✅ blog is now a single object
                return Response({
                    'data': {},
                    'message': 'You are not authorized to update this'
                }, status=status.HTTP_403_FORBIDDEN)

            serializer = BlogSerializers(blog, data=data, partial=True)

            if not serializer.is_valid():
                return Response({
                    'data': serializer.errors,
                    'message': 'Validation failed'
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()

            return Response({
                'data': serializer.data,
                'message': "Blog updated successfully"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({
                'data': {},
                'message': 'Something went wrong'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

     # DELETE: Delete a blog
    def delete(self, request):
        try:
            data = request.data
            blog = Blog.objects.filter(uid=data.get('uid')).first()

            if not blog:
                return Response({
                    'data': {},
                    'message': 'Invalid blog UID'
                }, status=status.HTTP_400_BAD_REQUEST)

            if request.user != blog.user:
                return Response({
                    'data': {},
                    'message': 'You are not authorized to delete this'
                }, status=status.HTTP_403_FORBIDDEN)

            blog.delete()  # ✅ fixed

            return Response({
                'data': {},
                'message': "Blog deleted successfully"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({
                'data': {},
                'message': 'Something went wrong'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CommentView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    # POST: Create a comment
    def post(self, request, blog_uid):
        try:
            blog = Blog.objects.get(uid=blog_uid)
            serializer = CommentSerializer(
                data=request.data,
                context={'request': request}
            )
            
            if not serializer.is_valid():
                return Response(
                    {"error": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer.save(blog=blog)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Blog.DoesNotExist:
            return Response(
                {"error": "Blog not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    # GET: List all comments for a blog
    def get(self, request, blog_uid):
        comments = Comment.objects.filter(blog__uid=blog_uid)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)




