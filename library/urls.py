from django.urls import path
from .views import BookListCreateView,BookedBookListCreateView,MemberListCreateView,BookRetriView,BookedBookRetriveview

urlpatterns = [
    path("book/", BookListCreateView.as_view()),
    path("book/<int:id>/", BookRetriView.as_view()),
    path("bookedbook/", BookedBookListCreateView.as_view()),
    path("bookedbook/<int:id>/", BookedBookRetriveview.as_view()),
    path("member/", MemberListCreateView.as_view())
]
