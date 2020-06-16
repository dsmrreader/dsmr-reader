from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic.base import TemplateView, View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import FormView

from dsmr_frontend.forms import NotificationReadForm
from dsmr_frontend.mixins import ConfigurableLoginRequiredMixin
from dsmr_frontend.models.message import Notification


class Notifications(ConfigurableLoginRequiredMixin, TemplateView):
    template_name = 'dsmr_frontend/notifications.html'

    def get_context_data(self, **kwargs):
        context_data = super(Notifications, self).get_context_data(**kwargs)
        context_data['notifications'] = Notification.objects.unread()
        return context_data


@method_decorator(csrf_exempt, name='dispatch')
class XhrMarkNotificationRead(LoginRequiredMixin, FormView):
    """ XHR view for marking one notification as read. """
    form_class = NotificationReadForm

    def form_valid(self, form):
        Notification.objects.filter(pk=form.cleaned_data['notification_id'], read=False).update(read=True)
        return JsonResponse({})


@method_decorator(csrf_exempt, name='dispatch')
class XhrMarkAllNotificationsRead(LoginRequiredMixin, View):
    """ XHR view for marking all notifications as read. """
    def post(self, request):
        Notification.objects.all().update(read=True)
        return JsonResponse({})
