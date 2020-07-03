from django.contrib.humanize.templatetags.humanize import naturaltime
from django.views.generic.base import RedirectView
from django.views.generic.base import View
from django.http import JsonResponse
from django.conf import settings

import dsmr_consumption.services


class XhrHeader(View):
    """ XHR view for fetching the dashboard header, displaying latest readings and price estimate, JSON response. """
    def get(self, request):
        data = dsmr_consumption.services.live_electricity_consumption()

        if data and data['timestamp']:
            data['timestamp'] = str(naturaltime(data['timestamp']))

        return JsonResponse(data)


class ReadTheDocsRedirectView(RedirectView):
    permanent = False
    subpage = None
    branch = settings.DSMRREADER_MAIN_BRANCH
    url = None

    def get(self, request, *args, **kwargs):
        self.url = 'https://dsmr-reader.readthedocs.io/{}/{}/{}'.format(
            request.LANGUAGE_CODE, self.branch, self.subpage
        )
        return super(ReadTheDocsRedirectView, self).get(request, *args, **kwargs)


class ChangelogRedirect(ReadTheDocsRedirectView):
    subpage = 'changelog.html'


class DocsRedirect(ReadTheDocsRedirectView):
    subpage = 'faq.html'


class FeedbackRedirect(ReadTheDocsRedirectView):
    subpage = 'contributing.html'


class DonationsRedirect(ReadTheDocsRedirectView):
    subpage = 'donations.html'


class V4UpgradeRedirect(ReadTheDocsRedirectView):
    subpage = 'faq/v4_upgrade.html'
    branch = 'v4'
