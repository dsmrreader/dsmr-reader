from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse_lazy

from dsmr_frontend.models.message import Notification


class NotificationRead(LoginRequiredMixin, RedirectView):
    """ View for marking notifications as read. """
    permanent = False
    url = reverse_lazy('frontend:dashboard')

    def post(self, request, *args, **kwargs):
        Notification.objects.filter(pk=self.request.POST['id']).update(read=True)
        return super(NotificationRead, self).post(request, *args, **kwargs)
