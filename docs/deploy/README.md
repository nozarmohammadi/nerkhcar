# Server config copies (not used by the app)
Copies of files that live outside git, for rebuilding the server after a failure.
- nerkhcar-api.service -> /etc/systemd/system/ (MemoryMax=120M, 127.0.0.1:8790)
- apache-nerkhcar.ir*.conf -> /etc/apache2/sites-available/ (a2ensite; certificates come from certbot)
Never put tokens or passwords here.
