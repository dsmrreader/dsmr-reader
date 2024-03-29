��    	      d               �   A   �   �   �   $   �  (   �       �   1  S     Q   k  �  �  C   �  �   �  #   �  &   �     #  �   6  i   1  [   �   Below there are some vhost samples to distinguish the difference. DSMR-reader can **not** create HTTPS for you, since it involves granting SSL certificates. However you can use `CertBot <https://certbot.eff.org/>`__ and `by Let's Encrypt <https://letsencrypt.org/>`__, to easily set it up. Default installation without HTTPS:: Installation after using Let's Encrypt:: Installation: HTTPS It's free to use and they're providing some guidance, which can be found here: `CertBot Debian / Nginx <https://certbot.eff.org/lets-encrypt/debianbuster-nginx>`__. Follow the guides over there and things should be taken care of. These are just Nginx vhost samples for your reference. Do **not** blindly use them! You should definitely use HTTPS when you're exposing DSMR-reader to the Internet. Project-Id-Version:  DSMR-reader
Report-Msgid-Bugs-To: Dennis Siemensma <github@dennissiemensma.nl>
POT-Creation-Date: 2022-06-07 21:23+0000
PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE
Last-Translator: Dennis Siemensma <github@dennissiemensma.nl>
Language: nl
Language-Team: Dennis Siemensma <github@dennissiemensma.nl>
Plural-Forms: nplurals=2; plural=(n != 1);
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit
Generated-By: Babel 2.10.1
 Hieronder staan van vhost-voorbeelden om het verschil te weergeven. DSMR-reader kan **geen** HTTPS voor je inschakelen, gezien er SSL-vertificaten voor nodig zijn. Je kunt echter wel `CertBot <https://certbot.eff.org/>`__ en `Let's Encrypt <https://letsencrypt.org/>`__ gebruiken om het relatief eenvoudig te regelen. Standaardinstallatie zonder HTTPS:: Installatie na gebruik Let's Encrypt:: Installatie: HTTPS Het is gratis om te gebruiken en er is goede ondersteuning, die je hier kunt terugvinden: `CertBot Debian / Nginx <https://certbot.eff.org/lets-encrypt/debianbuster-nginx>`__. Volg de instructies daar en uiteindelijk zou alles geregeld moeten worden. Dit zijn slechts wat Nginx-vhost voorbeelden voor je eigen referentie. Gebruik deze **niet** blindelings! Als je DSMR-reader bereikbaar maakt voor het Internet, zou je zeker HTTPS moeten gebruiken. 