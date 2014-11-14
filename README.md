telefab-website
===============

Site web du Téléfab

Organisation
---------------

Le dépôt est organisé en 3 parties :
* wordpress/ contient le code gérant le blog, le portfolio et la documentation
* django/ contient le code du lab pour la gestion du matériel, des écrans plasma et de l'ouverture du fablab (avec une API)
* tools/ contient des outils qui fonctionnent avec le site, comme le code Arduino pour ouvrir/fermer le fablab avec un bouton


Pré-requis
---------------

* Pour Python, les pré-requis sont dans le fichier django/pip_requirements (utiliser Python PIP)
* Pour PHP, le seul pré-requis particulier est le module CURL


Installation
---------------

* Configurer WordPress en copiant le fichier wordpress/wp-config-sample.php en wp-config.php
* Configurer Django en copiant le fichier django/telefab/telefab/local\_settings.sample.py en local\_settings.py
* Configurer le serveur pour utiliser PHP sur wordpress/ (URL : /)
* Configurer le serveur pour utiliser django sur django/telefab (URL : /lab)
* Dans django/telefab, lancer _python manage.py collectstatic_
* Dans django/telefab, lancer _python manage.py syncdb_