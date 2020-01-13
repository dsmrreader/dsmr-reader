from django.conf import settings
from django.views.generic.base import RedirectView


class ReadTheDocsRedirectView(RedirectView):
    permanent = False
    subpage = None
    url = None

    def get(self, request, *args, **kwargs):
        self.url = 'https://dsmr-reader.readthedocs.io/{}/{}/{}'.format(
            request.LANGUAGE_CODE, settings.DSMRREADER_MAIN_BRANCH, self.subpage
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
