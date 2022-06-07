��                        �  e   �     S  �   [  /   5     e  �   n     �  �     �   �  �   �  q   k  �   �  �   �     h  
   q     |  V   �     �  �   �  �   �	     1
     L
     T
  �   U  �      <   �     #  �   7  �    |   �     `    i  4   q     �  �   �     =  �   M  �       �  Y   �  �   U  �   (  	   �  	   �  '   �  `   �     ]  �   k  �        �     �  ^  �  �   >  @  �  B   #     f    {   :doc:`More information about using a remote datalogger here</how-to/installation/remote-datalogger>`. Backups Backups are created daily, but rotated weekly! So it's possible that, at some point, the backups get corrupted as well since they're overwritten each week. And eventually they will get synchronized to Dropbox as well. By default backups are created and written to:: Contents DSMR-reader does support automated backups, but since they are still stored on the same volatile storage, they can be corrupted as well. Data integrity Did you install using a monitor attached to the RaspberryPi and you don't know what address your device has? Just type ``ip a | grep inet`` and it should display an ip address, for example:: Enable password protection :doc:`in the configuration<configuration>` for the entire application, available in the Frontend settings in DSMR-reader as *"Force password login everywhere"*. If you are more technical savy, you could opt to either install the database or the entire application on a server with storage that tends to wear less. You can use the RaspberryPi are a remote datalogger, preventing a lot of issues. If you expose your application to the outside world or a public network, you might want to take additional steps: In this example the ip address is ``192.168.178.40``. If possible, you should assign a static ip address to your device in your router. This will make sure you will always be able to find the application at the same location. Now it's time to view the application in your browser to check whether the GUI works as well. Just enter the ip address or hostname of your RaspberryPi in your browser. Pitfalls Prevention Public webinterface warning Read this section carefully if you are using any volatile storage, such as an SD card. Reboot test Reducing the data throughput may help as well. :doc:`More information can be found in the FAQ (data section)</how-to/database/data-limits>`. SD cards' lifespan in this project vary from several weeks to some years, depending on the quality of the storage and the interval of telegrams sent by you smart meter. Setting up the application Storage The default storage on RaspberryPi's suffers greatly from this and can not be trusted to keep your data safe. Eventually the storage will get corrupted and either make your data inaccessible, or it pretends to write data, while not storing anything at all. The only thing you can do, is make sure to have your backups stored somewhere else, once in a while. Using Dropbox to sync your backups does not protect them of all harm! This project was designed to run on a RaspberryPi, but it affects the lifetime of the storage severely. The introduction of DSMR v5 smart meters strains the storage even more, due to the high amount of telegrams sent each second. Use :doc:`HTTPS when possible </how-to/installation/https>`. Viewing DSMR-reader You surely want to ``sudo reboot`` your device and check whether everything comes up automatically again with ``sudo supervisorctl status``. This will make sure your data logger 'survives' any power surges. Project-Id-Version:  DSMR-reader
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
 :doc:`Meer informatie over het gebruik van een remote datalogger is hier te vinden</how-to/installation/remote-datalogger>`. Back-ups Back-ups worden dagelijks gemaakt, echter worden deze ook wekelijks geroteerd! Dus op een gegeven moment kunnen ze na een week overschreven worden met een corrupte variant. En gezien ze ook naar Dropbox gesynchroniseerd kunnen worden, biedt dat ook geen garantie. Standaard worden back-ups hier naar toe geschreven:: Inhoudsopgave DSMR-reader heeft ondersteuning voor automatische back-ups. Echter, gezien deze op dezelfde opslag staan, kunnen deze ook corrupt raken. Dataintegriteit Heb je de applicatie geinstalleerd met een monitor aan je RaspberryPi en weet je het IP-adres niet? Typ in dat geval het volgende in en je krijgt het IP-adres te zien: ``ip a | grep inet`` , Bijvoorbeeld: Schakel applicatie-brede wachtwoordbescherming in :doc:`in de configuratie<configuration>`, beschikbaar in de Frontend-instellingen in DSMR-reader als *"Forceer overal inloggen met wachtwoord"*. Mocht je meer technisch aangelegd zijn. Je kunt overwegen om ofwel de database ofwel de hele applicatie op een andere server te installeren, waarbij de opslag minder last heeft van slijtage. Daarmee gebruik je de RaspberryPi als remote datalogger, wat een hoop problemen kan voorkomen. Wanneer je de applicatie aan het Internet koppelt wil je sowieso extra maatregelen nemen: In dit voorbeeld is het IP-adres ``192.168.178.40``. Het is aan te raden om je apparaat een vast IP-adres te geven in je router. Dit zorgt ervoor dat je de applicatie altijd op dezelfde locatie kan terugvinden. Dit is het moment om de applicatie te bekijken in je browser om te zien of alles naar behoren werkt. Vul het IP-adres van je RaspberryPi in je browser. Valkuilen Preventie Waarschuwing voor publiekelijke toegang Lees deze sectie aandachtig als je gebruikt maakt van onvoorspelbare opslag, zoals een SD-kaart. Herstart-test Het inperken van de gegevensdoorvoer kan hierbij ook helpen. :doc:`Meer informatie daarover vind je in de FAQ (data-sectie) </how-to/database/data-limits>`. De levensduur van SD-kaartjes varieert van enkele weken tot soms jaren, afhankelijk van de kwaliteit van deze en ook van de hoeveelheid telegrammen die je slimme meter stuurt. De applicatie instellen Gegevensopslag De standaardopslag van RaspberryPi's heeft hier erg veel last van en je kunt er niet op vertrouwen dat je gegevens daar veilig opgeslagen blijven. Vroeger of later geeft de opslag de geest en zorgt ervoor dat je ofwel niet meer bij je gegevens kunt, ofwel het lijkt dat de opslag goed functioneert, terwijl er in werkelijkheid niets opgeslagen wordt. Het enige wat hiertegen helpt is regelmatig ervoor zorgen dat je de back-up's ergens anders heen kopieert. Het gebruik van Dropbox garandeert ook geen bescherming! Dit project is ontworpen om op een RaspberryPi te draaien. Echter, dit heeft grote negatieve invloed op de levensduur van de opslagkaart. Daarnaast heeft de introductie van DSMR v5 slimme meters ervoor gezorgd dat de gegevensopslag nog meer onder druk staat. Dit komt doordat er elke seconde telegrammen worden gestuurd. Gebruik :doc:`HTTPS indien mogelijk </how-to/installation/https>`. DSMR-reader bekijken Herstart het apparaat met ``sudo reboot`` om te testen of alles automatisch opstart. Je zou na de herstart alles moeten zien draaien via ``sudo supervisorctl status``. Dit zorgt ervoor dat je datalogger eventuele stroomstoringen overleeft (of wanneer je zelf de stroom eraf haalt). 