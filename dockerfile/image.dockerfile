FROM ubuntu:20.04

WORKDIR /

RUN apt-get update
RUN apt-get install -f
RUN apt-get install -y wget
RUN apt-get install -y python3 python3-pip
RUN wget https://github.com/icode-pku/better_proxy/archive/refs/tags/v1.2.2.tar.gz

RUN tar -xavf ./v1.2.2.tar.gz
RUN mv better_proxy-1.2.2 better_proxy

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
