from django.views.generic.base import RedirectView


class ReadTheDocsRedirectView(RedirectView):
    permanent = False
    subpage = None
    url = None

    def get(self, request, *args, **kwargs):
        self.url = 'https://dsmr-reader.readthedocs.io/{}/latest/{}'.format(request.LANGUAGE_CODE, self.subpage)
        return super(ReadTheDocsRedirectView, self).get(request, *args, **kwargs)


class DocsRedirect(ReadTheDocsRedirectView):
    subpage = 'faq.html'


class FeedbackRedirect(ReadTheDocsRedirectView):
    subpage = 'contributing.html'
