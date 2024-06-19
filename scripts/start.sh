#! /bin/bash

cd ../

pwd

# 构建镜像
sudo docker build -t better_proxy_image:v1.2.1 -f dockerfile/image.dockerfile  . 

# 构建容器 运行前，需要配置自定义要映射到容器/better_proxy/config的本地目录:[/home/user_name/workspace/better_proxy/config]
sudo docker run -dt --name better_proxy_container_v121 -p 10809:10809  -v /home/user_name/workspace/better_proxy/config:/better_proxy/config  better_proxy_image:v1.2.1 

echo "build docker container successfully..."
echo "Next you need export the http_proxy and test the net..."

# export http_proxy="http://127.0.0.1:10809"
# export https_proxy="http://127.0.0.1:10809"
# curl www.google.com

