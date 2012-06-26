telefab-website
===============

Site web du Téléfab

Installation
---------------

* Configurer WordPress en copiant le fichier wordpress/wp-config-sample.php en wp-config.php
* Configurer Django en copiant le fichier django/telefab/telefab/local\_settings.sample.py en local\_settings.py
* Configurer le serveur pour utiliser PHP sur wordpress/ (URL : /)
* Configurer le serveur pour utiliser django sur django/telefab (URL : /lab)
* Dans django/telefab, lancer _python manage.py syncdb_