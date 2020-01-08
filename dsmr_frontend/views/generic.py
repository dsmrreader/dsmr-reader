from django.views.generic.base import RedirectView


class ReadTheDocsRedirectView(RedirectView):
    permanent = False
    subpage = None
    url = None

    def get(self, request, *args, **kwargs):
        self.url = 'https://dsmr-reader.readthedocs.io/{}/v2/{}'.format(request.LANGUAGE_CODE, self.subpage)
        return super(ReadTheDocsRedirectView, self).get(request, *args, **kwargs)


class ChangelogRedirect(ReadTheDocsRedirectView):
    subpage = 'changelog.html'


class DocsRedirect(ReadTheDocsRedirectView):
    subpage = 'faq.html'


class FeedbackRedirect(ReadTheDocsRedirectView):
    subpage = 'contributing.html'


class DonationsRedirect(ReadTheDocsRedirectView):
    subpage = 'donations.html'


class V3UpgradeRedirect(RedirectView):
    permanent = False
    subpage = None
    url = None

    def get(self, request, *args, **kwargs):
        # Overwrite the entire URL, because we need it to point to v3 branch.
        self.url = 'https://dsmr-reader.readthedocs.io/{}/v3/faq/v3_upgrade.html'.format(request.LANGUAGE_CODE)
        return super(V3UpgradeRedirect, self).get(request, *args, **kwargs)
