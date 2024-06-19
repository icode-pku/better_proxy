# 项目名称：BETTER_PROXY
该项目为一个服务器网络自动切换工具，旨在Ubuntu系统20.04/22.04本地服务器上进行部署，实现全自动定时切换外部服务器网络，保证系统访问网络良好

## 目录
- [项目名称：BETTER\_PROXY](#项目名称better_proxy)
  - [目录](#目录)
  - [一、本项目开发环境:](#一本项目开发环境)
  - [二、版本更新：](#二版本更新)
    - [1.0.0 版本发布：](#100-版本发布)
    - [1.1.0 版本更新内容：](#110-版本更新内容)
    - [1.1.1 版本更新内容：](#111-版本更新内容)
    - [1.2.1 版本更新内容：](#121-版本更新内容)
  - [三、项目使用流程](#三项目使用流程)
    - [配置config目录中的文件](#配置config目录中的文件)
    - [基于dockerfile构建镜像](#基于dockerfile构建镜像)
    - [基于镜像构建容器](#基于镜像构建容器)
    - [设置本地端口](#设置本地端口)
    - [测试网络是否良好](#测试网络是否良好)
    - [附：构建镜像与容器脚本](#附构建镜像与容器脚本)



## 一、本项目开发环境: 
1）Ubuntu22.04 64位  
2）python 3.10

## 二、版本更新：

### 1.0.0 版本发布：
初始版本发布功能如下：

1）获取用户定义的server urls并解析；

2）自动多线程测试各个网络的延迟，选择切换为延迟最低的网络；

3）每隔一定时间进行步骤2。

### 1.1.0 版本更新内容：
添加功能：每次网络切换时自动更新用户自定义的配置文件。

### 1.1.1 版本更新内容：
修复已发现的bug。

### 1.2.1 版本更新内容：
添加功能：网络缓存备份，用于备用网络切换，提高网络稳定性。

## 三、项目使用流程

### 配置config目录中的文件
首先你需要从本项目上下载dockerfile文件和config目录文件放置在你的linux系统中/home下的用户目录中：<br>
1）下载完成后config目录的放置路径便是下面步骤中的[host_config_path]，<br>

2）在运行项目前，你需要配置config/py_config.json文件；
这里给出了模板参数：<br>
    "url": "http://example.com", //表示获取存储所有服务器网络信息的url，必填参数<br>
    "exc_sleep_time": 86400, //表示切换网络的间隔时间（秒）<br>
    "check_net_well_time": 3600, //表示检测网络的间隔时间（秒）<br>
    "host_port": 10809, //默认端口号，不要轻易更改，多次请求获取存储所有网络信息的url网址失败，并且在你没有内部服务器网络时，如果你在本机127.0.0.1上别的端口号设置有网络，可以更改这一端口<br>
    "request_sleep_time": 1800, //请求网址失败停止等待时间（秒）<br>
    "help_proxy": "http://example.com" //多次请求获取存储所有服务器网络信息的url网址失败时可以选择使用你个人的网络进行再次请求，若没有内部服务器网络，请务必删除"help_proxy"这一键值对<br>

3）config/default_config.json已经配置好了，该文件仅用于存储项目初始运行所使用的网络配置信息，当然你也可以有自己的配置文件进行内容参数替换，后续网络切换均会覆盖这一配置文件。<br>


### 基于dockerfile构建镜像
命令格式：<br>
```
sudo docker build -t [your_image_name] -f [your_dockerfile_path]  . 
```
这里注意命令末尾有个  **.**

说明：<br>
**[your_image_name]**：为你所要构建镜像的名称<br>
**[your_dockerfile_path]**：为你要构建镜像所使用的dockerfile的路径<br>

示例：<br>
```
sudo docker build -t demo_image_name -f dockerfile/image.dockerfile  . 
```

注：如果构建时ubuntu20.04下载不了，你可以先运行如下命令：
```
docker pull ubuntu:20.04
```

如果需要docker配置代理拉取镜像，参照如下方法：<br>
**创建目录和文件**
```
mkdir /etc/systemd/system/docker.service.d/ 
sudo vim /etc/systemd/system/docker.service.d/http-proxy.conf
```
**在http-proxy.conf中添加内容：**

以下为示例，需要换成你自己的代理ip和端口
```
[Service]
Environment="HTTP_PROXY=http://192.168.2.199:8118"
Environment="HTTPS_PROXY=http://192.168.2.199:8118"
# 下面是不走代理的时候，可以不加。有私有仓库时，可以用来加私有仓库
# Environment="NO_PROXY=localhost,127.0.0.1"
```
**重启docker**
```
sudo systemctl daemon-reload
sudo systemctl restart docker
```

**检查代理**

```
# 可以看到刚才配置的代理
docker info | grep -i proxy
```

### 基于镜像构建容器
命令格式：<br>
```
sudo docker run -dt --name [your_container_name] -p [host_port]:10809  -v [host_config_path]:/better_proxy/config [your_image_name] 
```
说明：<br>
**[your_container_name]**：为你要构建容器的名称<br> 
**[host_port]**：为你要进行映射的本机端口<br>
**[host_config_path]**：为你要进行映射的网络工具配置文件所在目录路径<br>
**[your_image_name]**：为上一步骤构建镜像的名称<br>

示例：<br>
```
sudo docker run -dt --name demo_container_name -p 10809:10809  -v /home/Niko/config:/better_proxy/config  demo_image_name 
```
参数说明：<br>
-p：将主机端口**10809**映射到所构建docker容器的**10809**端口，若主机端口10809(默认选择)已被占用，可改用其他端口号<br>
-v：将主机中网络配置文件所在目录/home/Niko/config映射到所构建docker容器的/better_proxy/config目录<br>

### 设置本地端口
命令格式：<br>
```
export http_proxy="http://127.0.0.1:[host_port]"
export https_proxy="http://127.0.0.1:[host_port]"
```
说明：<br>
**[host_port]**：要与上面步骤设置的主机端口保持一致<br>

示例：
```
export http_proxy="http://127.0.0.1:10809"
export https_proxy="http://127.0.0.1:10809"
```
### 测试网络是否良好 

如果上面步骤均没有问题，便可以测试网络了，这里以google为例<br>
示例：<br>
```
curl www.google.com 
```

### 附：构建镜像与容器脚本 
构建脚本位于scripts/start.sh

需要执行以下命令：
```
cd scripts/
chmod +x start.sh
```
注：在配置好config信息和成功拉取到Ubuntu：20.04镜像后才能使用

执行脚本之前，需要修改一下里边映射到容器config目录的**主机config目录**
```
./start.sh
```