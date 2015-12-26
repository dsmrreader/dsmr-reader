from django.views.generic.base import TemplateView

from dsmr_stats import mixins


class Dashboard(mixins.DashboardMixin, TemplateView):
    template_name = 'dsmr_stats/dashboard.html'


class History(mixins.HistoryMixin, TemplateView):
    template_name = 'dsmr_stats/history.html'


class Statistics(mixins.StatisticsMixin, TemplateView):
    template_name = 'dsmr_stats/statistics.html'
