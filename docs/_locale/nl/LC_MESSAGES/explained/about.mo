��    1      �              ,  b   -  "   �  b   �  i     6   �  6   �  A   �  5   0  D   f  M   �  A   �     ;     A  @   S  �   �     z     �     �     �  	   �     �     �     �  Z   �  	   4     >  �   J  ?   �     	  p   )	     �	  S   �	     �	  
   
     
  J   "
  �   m
  A     �   S  �   �  h   �  �     J   �  �     B   �     �  7   �  �   3  �  �  f   �      ;  f   \  e   �  @   )  B   j  L   �  8   �  M   3  W   �  O   �     )     .  b   ?  	  �     �     �     �     �  	   �     �     �     �  ^        o     u  �   �  Q        `  }   n     �  R   �     K     ]     j  C   q  z   �  ?   0  �   p  �     {   �  �   `  O     �   ^  P        c  G   j  �   �   **Code**: A `supported <https://devguide.python.org/#status-of-python-branches>`__ Python version. **Data transfer protocol support** **Database**: A `supported <https://www.postgresql.org/support/versioning/>`__ PostgreSQL version. **Disk space**: 1+ GB - Depending on your smart meter and whether how many readings you want to preserve. **For datalogger only**: *Any* RaspberryPi or similar. **For full DSMR-reader**: *RaspberryPi 3+* or similar. **MQTT**: Push data from DSMR-reader to a generic message broker. **OS**: ``Raspbian OS`` or similar (or using Docker). **REST API**: Pull data from DSMR-reader from a generic HTTP client. **REST API**: Push (telegram) data from a generic HTTP client to DSMR-reader. A smart meter supporting DSMR versions: ``v2`` / ``v4`` / ``v5``. About About DSMR-reader Allow you to export your data to other systems or third parties. Any integration should be possible this way, either using generic scripts or even :doc:`plugins</reference/plugins>`. DSMR-reader only supports the generic protocols above and cannot support every individual integration possible. Archive Compare Configuration Contents Dashboard Energy contracts Export Hardware requirements If your meter supports it, you can also see your gas consumption and electricity returned. Languages Live graphs Note that this project is built with `Django <https://www.djangoproject.com/>`__, which decides which Python/DB versions are actually supported. P1 telegram cable (or a network socket when using ``ser2net``). Project goals Provide a tool to easily extract, store and visualize data transferred by the DSMR protocol of your smart meter. Screenshots Shows the 'health' of the application and provides a lot of background information. Software requirements Statistics Status Summary of all your contracts and the amount of energy consumed/generated. The archive allows you to scroll through all historisch data captured by the application. All data can be viewed on different levels: by day, by month and by year. The configuration page is the entrypoint for the admin interface. The dashboard displays the latest information regarding the consumption of today. You can view the total consumption for the current month and year as well. The entire application and its code is written and documented in English. The interface is translated into Dutch and will be enabled automatically, depending on your browser's language preference. The live graphs plots the most recent data available, depending on the capabilities of your smart meter. This page allows you to simply compare two days, months or years with each other. It will also display the difference between each other as a percentage. This page displays a summary of your average daily consumption and habits. This page displays your meter positions and statistics provided by the DSMR protocol. You can also find the number of readings stored and any excesses regarding consumption. This pages allows you to export all day or hour statistics to CSV. Trends You can also easily check for DSMR-reader updates here. You can type any topic or setting you're searching for, as it should pop up with clickable deeplink to the admin panel. Or you can just skip it this page and continue directly to the admin panel. Project-Id-Version:  DSMR-reader
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
 **Code**: Een `ondersteunde <https://devguide.python.org/#status-of-python-branches>`__ Python-versie. **Ondersteuning dataoverdracht** **Database**: Een `ondersteunde <https://www.postgresql.org/support/versioning/>`__ PostgreSQL-versie. **Schijfruimte**: 1+ GB - Afhankelijk van je slimme meter en de hoeveelheid metingen je wilt bewaren. **Voor alleen-datalogger**: *Elke* RaspberryPi of vergelijkbaar. **Voor volledige DSMR-reader**: *RaspberryPi 3+* of vergelijkbaar. **MQTT**: Duw gegevens vanuit DSMR-reader naar een generieke message broker. **OS**: ``Raspbian OS`` of vergelijkbaar (of via Docker) **REST API**: Trek gegevens uit DSMR-reader vanuit een generieke HTTP-client. **REST API**: Duw (telegram)gegevens vanuit een generieke HTTP-client naar DSMR-reader. Een slimme meter met ondersteuning voor DSMR-versies: ``v2`` / ``v4`` / ``v5``. Over Over DSMR-reader Beheer je eigen gegevens, om ze bijvoorbeeld te exporteren naar andere systemen of derde partijen. In principe is elke integratie hierdoor mogelijk, via ofwel generieke scripts of zelfs :doc:`plugins</reference/plugins>`. DSMR-reader ondersteunt echter alleen de generieke protocollen hierboven en kan niet elke mogelijke individuele variant (intern) ondersteunen. Archief Vergelijken Configuratie Inhoudsopgave Dashboard Energiecontracten Export Hardwarevereisten Je ziet hier ook je gasverbruik en teruglevering elektriciteit, mits je meter dat ondersteunt. Talen Live grafieken N.B.: Dit project is gebouwd met `Django <https://www.djangoproject.com/>`__, wat de uiteindelijk ondersteunde Python/DB-versies bepaalt. Kabel voor uitlezen P1-poort (of een netwerksocket via bijvoorbeeld ``ser2net``). Projectdoelen Een tool aanbieden waarmee je eenvoudig gegevens uit je slimme meter via het DSMR-protocol uitleest, opslaat en visualiseert. Screenshots Toont de status van de applicatie en verwijst naar een hoop achtergrondinformatie. Softwarevereisten Statistieken Status Overzicht van al je energiecontracten en het bijbehorende verbruik. In het archief kun je door alle historische data heen bladeren. Je kunt de gegevens bekijken op dag-, maand- of jaarbasis. De configuratiepagina is de toegangspoort tot het adminportaal. Het dashboard weergeeft de meeste actuele informatie over je verbruik vandaag. Je ziet hier ook het totale verbruik van de huidige maand en jaar. De gehele applicatie, en bijbehorende code, is in het Engels geschreven. De grafische interface is echter ook in het Nederlands beschikbaar. Deze wordt  automatisch getoond, afhankelijk van de taalinstelling in je webbrowser. De Live Grafieken pagina toont de meest recente beschikbare gegevens, afhankelijk van de mogelijkheden van je slimme meter. Deze pagina stelt je in staat om simpelweg twee dagen, maanden of jaren met elkaar te vergelijken. Daarnaast worden de verschillen tussen de twee weergegeven als percentage. Deze pagina weergeeft een samenvatting van je dagelijkse verbruik en gewoontes. Deze pagina weergeeft je huidige meterstanden en statistieken volgens het DSMR-protocol. Je kunt hier ook het totaal aantal opgeslagen metingen vinden, evenals excessief verbruik. Deze pagina staat je toe om alle uur- en dagstatistieken te exporteren naar CSV. Trends Je kunt hier eveneens eenvoudig controleren op updates van DSMR-reader. Je kunt hier elk onderwerp of instelling waarnaar je op zoek bent intypen, om vervolgens een popup te krijgen met een klikbare link, direct naar het juiste onderdeel binnen het adminportaal. 