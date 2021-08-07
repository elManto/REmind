# Dockerization

Actually we do not use docker since we already rely on a VM infrastructure. But anyway it is possible to deploy the dockerized version by:

1. docker build --no-cache -t img\_name .
2. docker run -p 5000:4000 -it -v /home/mantovan/remind2/:/flask\_website/instance/ img\_name
