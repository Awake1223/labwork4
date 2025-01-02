from django.urls import path
from .views import index, delete_article, edit_article, search_articles

urlpatterns = [
    path('', index, name='index'),
    path('delete/<int:article_id>/', delete_article, name='delete_article'),
    path('edit/<int:article_id>/', edit_article, name='edit_article'),
    path('search/', search_articles, name='search_articles'),

]
