from django.urls import path

from . import views

app_name = "histories"

urlpatterns = [
    path("", views.HistoryListView.as_view(), name="list"),
    path("create/", views.HistoryCreateView.as_view(), name="create"),
    path("<int:pk>/", views.HistoryDetailView.as_view(), name="detail"),
    path("<int:pk>/update/", views.HistoryUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.HistoryDeleteView.as_view(), name="delete"),
]
