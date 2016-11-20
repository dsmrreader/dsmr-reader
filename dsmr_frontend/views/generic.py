from django.views.generic.base import RedirectView


class DocsRedirect(RedirectView):
    permanent = False
    url = None

    def get(self, request, *args, **kwargs):
        self.url = 'https://dsmr-reader.readthedocs.io/{}/latest/'.format(request.LANGUAGE_CODE)
        return super(DocsRedirect, self).get(request, *args, **kwargs)
