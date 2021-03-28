��          �            h  	   i  '   s  g   �  :     ^   >  �   �        $   �  8   �  /   �  U   .  f   �  X   �  N   D  �  �     J  *   S  s   ~  C   �  n   6  �   �  �   :	  '   �	  9   �	  ;   7
  ]   s
  }   �
  d   O  G   �         	                                                      
                 Attention Database: Restore a backup (PostgreSQL) Doing so **will** cause trouble with duplicate data/ID's and **break** your installation at some point. First check whether situation A or B applies to you below. If you are still in the process of reinstalling DSMR-reader and just executed these commands:: If you do encounter errors while restoring the backup in an **empty** database, create an issue at GitHub and **do not continue**. If you just finished reinstalling DSMR-reader but **did not** restore the backup and you want to **overwrite** the data in it:: Now continue the installation guide. Situation A: Already finished DSMR-reader reinstallation Situation B: Currently reinstalling DSMR-reader The steps below replace any existing data stored in the database and is irreversible! You cannot merge a database backup with an existing installation containing data you want to preserve! You should **not** see any errors regarding duplicate data or existing ID's or whatever. Your database **should** still be empty and this will import any backup made:: Project-Id-Version: DSMR Reader
Report-Msgid-Bugs-To: Dennis Siemensma <github@dennissiemensma.nl>
Last-Translator: Dennis Siemensma <github@dennissiemensma.nl>
Language: nl
Language-Team: Dennis Siemensma <github@dennissiemensma.nl>
Plural-Forms: nplurals=2; plural=(n != 1);
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit
Generated-By: Babel 2.9.0
X-Generator: Poedit 2.0.6
PO-Revision-Date: 
 Attentie Database: Back-up terugzetten (PostgreSQL) Doorgaan zorgt er **gegarandeerd** voor dat er **problemen** komen met dubbele gegevens/ID's op een bepaald moment. Kijk eerst of A ofwel B hieronder van toepassing is op je situatie. Als je nog steeds bezig bent met de herinstallatie van DSMR-reader en je net deze commando's hebt uitgevoerd:: Mocht je bij het terugzetten van de back-up in een **lege** database toch fouten tegenkomen, maak dan een issue aan op GitHub en **ga niet verder**. Als je DSMR-reader opnieuw hebt geinstalleerd en **niet** de backup hebt teruggezet, maar wel alle gegevens in de nieuwe database wilt **overschrijven**:: Ga nu verder met de installatiestappen. Situatie A: DSMR-reader al helemaal opnieuw geinstalleerd Situatie B: Nog bezig met de herinstallatie van DSMR-reader De stappen hieronder overschrijven alle bestaande gegevens in de database en is onomkeerbaar! Je kunt helaas niet een databasebackup samenvoegen met een bestaande installatie, waar gegevens in staan die je wilt bewaren. Je zou **geen** fouten moeten zien m.b.t dubbele gegevens en/of bestaande ID's of iets soortgelijks. Je database **zou** nog leeg moeten zijn en dit importeert een backup:: 