Installation: HTTPS
===================

You should definitely use HTTPS when you're exposing DSMR-reader to the Internet.

DSMR-reader can **not** create HTTPS for you, since it involves granting SSL certificates.
However you can use `CertBot <https://certbot.eff.org/>`__ and `by Let's Encrypt <https://letsencrypt.org/>`__, to easily set it up.

It's free to use and they're providing some guidance, which can be found here: `CertBot Debian / Nginx <https://certbot.eff.org/lets-encrypt/debianbuster-nginx>`__.
Follow the guides over there and things should be taken care of.

----

Below there are some vhost samples to distinguish the difference.

.. warning::

    These are just Nginx vhost samples for your reference. Do **not** blindly use them!

Default installation without HTTPS::

    upstream dsmr-webinterface {
        server unix:///tmp/gunicorn--dsmr_webinterface.socket fail_timeout=0;
    }

    server {
        listen      80;
        server_name _;  # No hostname available? Just use the default underscore here for wildcard matching.

        location /static {
            alias /var/www/dsmrreader/static;
        }

        location / {
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $http_host;
            proxy_redirect off;
            proxy_pass http://dsmr-webinterface;
        }
    }


Installation after using Let's Encrypt::

    upstream dsmr-webinterface {
        server unix:///tmp/gunicorn--dsmr_webinterface.socket fail_timeout=0;
    }

    server {
        listen      443 ssl http2;
        server_name hostname.com;

        ssl_certificate     /etc/letsencrypt/live/hostname.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/hostname.com/privkey.pem;
        ssl_protocols       TLSv1 TLSv1.1 TLSv1.2;
        ssl_ciphers         HIGH:!aNULL:!MD5;

        location /static {
            alias /var/www/dsmrreader/static;
        }

        location / {
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $http_host;
            proxy_redirect off;
            proxy_pass http://dsmr-webinterface;
        }
    }
