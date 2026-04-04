from django.urls import path

from . import views

app_name = "review"

urlpatterns = [
    path("", views.my_queue, name="my_queue"),
    path("logout/", views.logout_view, name="logout"),
    path("stem/<int:stem_id>/", views.review_stem, name="review_stem"),
]
