FROM ubuntu:20.04

WORKDIR /

RUN apt-get update
RUN apt-get install -f
RUN apt-get install -y wget
RUN apt-get install -y python3 python3-pip
RUN wget https://github.com/icode-pku/better_proxy/archive/refs/tags/v1.2.1.tar.gz

RUN tar -xavf ./v1.2.1.tar.gz
RUN mv better_proxy-1.2.1 better_proxy

WORKDIR /better_proxy

RUN pip3 install -r requirement.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

ENV http_proxy="http://127.0.0.1:10809"
ENV https_proxy="http://127.0.0.1:10809"

RUN chmod +x /better_proxy/xray_bin/xray

RUN echo "start to run better_proxy"

ENTRYPOINT ["/bin/bash", "-c"]

# reflect to /better_proxy/config/

### -v $host/config:/better_proxy/config
CMD ["python3 main.py"]

# sudo docker build --no-cache  -t better_proxy_test -f dockerfile/image.dockerfile  .  # 基于dockerfile构建镜像
# sudo docker run -dt --name our_proxy -p 10909:10809  -v /home/niupeiyu/config:/better_proxy/config  better_proxy_test   # 构建容器

# export http_proxy="http://127.0.0.1:10909"
# export https_proxy="http://127.0.0.1:10909"
# curl www.google.com 
