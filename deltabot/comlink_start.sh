sudo docker pull ghcr.io/swgoh-utils/swgoh-comlink:1.12.0
sudo docker stop swgoh-comlink
sudo docker rm swgoh-comlink
sudo docker run --name swgoh-comlink \
  -d \
  --restart always \
  --env APP_NAME=deltabot \
  -p 3200:3000 \
  ghcr.io/swgoh-utils/swgoh-comlink:1.12.0

#  --memory-swap="2g" \
#  --memory="500m" \

