# 项目名称：better_proxy

## 一、本项目开发环境: 
1）Ubuntu22.04 64位  
2）python 3.10

## 二、版本更新：

## 1.0.0 版本发布：
该项目为一个网络自动切换工具，功能如下：

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

 ### 基于dockerfile构建镜像
命令格式：
```
sudo docker build -t [your_image_name] -f [your_dockerfile_path]  . 
```
这里注意命令末尾有个  **.**

说明：
**[your_image_name]**：为你所要构建镜像的名称
**[your_dockerfile_path]**：为你要构建镜像所使用的dockerfile的路径

示例：
```
sudo docker build -t demo_image_name -f dockerfile/image.dockerfile  . 
```
### 基于镜像构建容器
命令格式：
```
sudo docker run -dt --name [your_container_name] -p [host_port]:10809  -v [host_config_path]:/better_proxy/config [your_image_name] 
```
说明：
**[your_container_name]**：为你要构建容器的名称
**[host_port]**：为你要进行映射的本机端口
**[host_config_path]**：为你要进行映射的网络工具配置文件所在目录路径
**[your_image_name]**：为上一步骤构建镜像的名称

示例：
```
sudo docker run -dt --name demo_container_name -p 10809:10809  -v /home/Niko/config:/better_proxy/config  demo_image_name 
```
参数说明：
-p：将主机端口**10809**映射到所构建docker容器的**10809**端口，若主机端口10809(默认选择)已被占用，可改用其他端口号
-v：将主机中网络配置文件所在目录/home/Niko/config映射到所构建docker容器的/better_proxy/config目录

### 设置本地端口
命令格式：
```
export http_proxy="http://127.0.0.1:[host_port]"
export https_proxy="http://127.0.0.1:[host_port]"
```
说明：
**[host_port]**：要与上面步骤设置的主机端口保持一致

示例：
```
export http_proxy="http://127.0.0.1:10809"
export https_proxy="http://127.0.0.1:10809"
```
### 测试网络是否良好 

如果上面步骤均没有问题，便可以测试网络了，这里以google为例
示例：
```
curl www.google.com 
```

