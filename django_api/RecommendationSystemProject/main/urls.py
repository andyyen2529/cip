from django.urls import path
from . import views

urlpatterns = [
    path('demo1', views.demo1),
    path('demo2', views.demo2),
    path('demo3/', views.getRecommendCategories, name='getRecommendCategories'),
    path('demo4', views.demo4),
    path('recommend_categories/ajax_calls/', views.getRecommendCategoriesAjax, name='getRecommendCategoriesAjax'),
    path('recommend_categories/audio_file/ajax_calls/', views.getRecommendCategoriesAjaxByAudioFile, name='getRecommendCategoriesAjaxByAudioFile'),
    path('recommend_categories/audio/ajax_calls/', views.getRecommendCategoriesAjaxByAudio, name='getRecommendCategoriesAjaxByAudio'),
]