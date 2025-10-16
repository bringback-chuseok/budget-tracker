# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .models import Histories


class HistoryCreateView(CreateView):
    model = Histories
    template_name = "histories/history_form.html"
    fields = ["account_id", "amount", "balance", "desc", "inout_type", "transact_type"]
    success_url = reverse_lazy("histories:list")


class HistoryListView(ListView):
    model = Histories
    template_name = "histories/history_list.html"
    context_object_name = "histories"
    ordering = ["-transacted_at"]


class HistoryDetailView(DetailView):
    model = Histories
    template_name = "histories/history_detail.html"
    context_object_name = "history"


class HistoryUpdateView(UpdateView):
    model = Histories
    template_name = "histories/history_form.html"
    fields = ["amount", "balance", "desc", "inout_type", "transact_type"]
    success_url = reverse_lazy("histories:list")


class HistoryDeleteView(DeleteView):
    model = Histories
    template_name = "histories/history_confirm_delete.html"
    success_url = reverse_lazy("histories:list")
