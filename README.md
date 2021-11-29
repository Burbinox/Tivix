# Tivix

To run app you need to clone repo and create docker image:

```
docker build -t myimage .
```
And then run image:
```
docker run -d --name mycontainer -p 80:80 myimage
```

App will be available in adres: http://0.0.0.0:80
