
From: https://www.digitalocean.com/community/tutorials/how-to-deploy-a-scalable-and-secure-django-application-with-kubernetes

Note internal ports need to be 0.0.0.0:8080, ie `python manage.py runserver 0.0.0.0:8080`.

Currently using extremely insecure settings.py for proof of concept. Must fix, and change ALLOWED_HOSTS

Updating:

1) docker build -t simplesignal .
2) docker tag simplesignal:latest matthewthomasroche/simplesignal:latest
3) docker push matthewthomasroche/simplesignal:latest
4) Restart containers
