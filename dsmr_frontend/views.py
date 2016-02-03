from django.views.generic.base import TemplateView

from dsmr_frontend import mixins


class Dashboard(mixins.DashboardMixin, TemplateView):
    template_name = 'dsmr_frontend/dashboard.html'


class History(mixins.HistoryMixin, TemplateView):
    template_name = 'dsmr_frontend/history.html'


class Statistics(mixins.StatisticsMixin, TemplateView):
    template_name = 'dsmr_frontend/statistics.html'
