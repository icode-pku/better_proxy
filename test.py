import json
import requests
from requests.exceptions import Timeout
import base64
from urllib.parse import unquote
import subprocess
import time
import os
import speedtest


# 解析trojan url关键参数 return url_trojan_dict
def read_trojan(url_trojan):
    url_trojan_dict = dict()
    url_trojan_dict["address"] = url_trojan.split("@")[1].split(":")[0]
    url_trojan_dict["port"] = int(url_trojan.split("@")[1].split(":")[1].split("?")[0])
    url_trojan_dict["password"] = url_trojan.split("@")[0].split("//")[1]
    return url_trojan_dict


# 填充trojan 关键参数 return the_total_dict
def write_trojan_args(url_trojan_dict):
    the_total_dict = dict()  # config.json中“outbounds”list中的第一个dict元素
    the_total_dict["tag"] = "proxy"
    the_total_dict["protocol"] = "trojan"
    the_total_dict["settings"] = {
        "servers": [
            {
                "address": url_trojan_dict["address"],
                "method": "chacha20",
                "ota": False,
                "password": url_trojan_dict["password"],
                "port": url_trojan_dict["port"],
                "level": 1,
                "flow": "",
            }
        ]
    }
    the_total_dict["streamSettings"] = {
        "network": "tcp",
        "security": "tls",
        "tlsSettings": {
            "allowInsecure": False,
            "serverName": url_trojan_dict["address"],
            "show": False,
        },
    }
    the_total_dict["mux"] = {"enabled": False, "concurrency": -1}
    return the_total_dict


# 解析vmess url关键参数 return url_vmess_dict
def read_vmess(url_vmess):
    url_vmess_dict = dict()
    url_vmess_dict["address"] = url_vmess.split("@")[1].split(":")[0]
    url_vmess_dict["port"] = int(url_vmess.split("@")[1].split(":")[1].split("/")[0])
    url_vmess_dict["id"] = url_vmess.split("//")[1].split(":")[0]
    url_vmess_dict["alterId"] = int(url_vmess.split("@")[0].split(":")[2])
    url_vmess_dict["path"] = url_vmess.split("path=")[1].split("&")[0]
    return url_vmess_dict


# 填充trojan 关键参数 return the_total_dict
def write_vmess_args(url_vmess_dict):
    the_total_dict = dict()  # config.json中“outbounds”list中的第一个dict元素
    the_total_dict["tag"] = "proxy"
    the_total_dict["protocol"] = "vmess"
    the_total_dict["settings"] = {
        "vnext": [
            {
                "address": url_vmess_dict["address"],
                "port": url_vmess_dict["port"],
                "users": [
                    {
                        "id": url_vmess_dict["id"],
                        "alterId": url_vmess_dict["alterId"],
                        "email": "t@t.tt",
                        "security": "auto",
                    }
                ],
            }
        ]
    }
    if url_vmess_dict["path"] == "/":
        the_total_dict["streamSettings"] = {
            "network": "ws",
            "wsSettings": {
                "path": "/",
                "headers": {
                    "Host": "25a22a928d882c4614d03a2d3135280e.mobgslb.tbcache.com"
                },
            },
        }
    else:  # url_vmess_dict["path"]=""
        the_total_dict["streamSettings"] = {
            "network": "ws",
            "wsSettings": {"headers": {}},
        }
    the_total_dict["mux"] = {"enabled": False, "concurrency": -1}
    return the_total_dict


# 写回config.json
def write_config_json(the_total_dict, config_path):
    # 读取JSON文件
    with open(config_path, "r") as f:
        data = json.load(f)

    # 修改数据
    data["outbounds"][0] = the_total_dict

    # 写入JSON文件
    with open(config_path, "w") as f:
        json.dump(
            data,
            f,
            indent=4,
        )
    pass


# 测量延迟
def measure_latency(proxy):
    # 构建目标 URL
    url = "https://www.google.com"  # 要访问的目标网站
    try:
        # 发送请求
        response = requests.get(
            url, verify=False, proxies={"http": proxy, "https": proxy}
        )
        # 测量延迟
        print("latency test started...")
        if response.status_code == 200:
            # 打印响应内容
            # print("response2 text:",response.text)
            # 打印延迟
            print(int(response.elapsed.total_seconds() * 1000))
            return int(response.elapsed.total_seconds() * 1000)
        else:
            print(response.reason)
            return -1
    except:
        raise Exception("latency test time out...")


# 测试带宽 demo func1
def measure_bandwidth():
    print("准备测试ing...")
    # 创建实例对象
    test = speedtest.Speedtest()
    # 获取可用于测试的服务器列表
    test.get_servers()
    # 筛选出最佳服务器
    best = test.get_best_server()
    print("正在测试ing...")
    # 下载速度
    download_speed = int(test.download() / 1024 / 1024)
    # 上传速度
    upload_speed = int(test.upload() / 1024 / 1024)
    # 输出结果
    print("下载速度：" + str(download_speed) + " Mbits")
    print("上传速度：" + str(upload_speed) + " Mbits")


# 测试带宽 demo func2
def test_proxy_bandwidth(proxy):
    # 测试使用的URL
    test_url = "https://www.google.com"

    # 分别测试k次，以便于计算平均带宽
    k = 2
    download_times = []
    for _ in range(k):
        start_time = time.time()
        response = requests.get(test_url, proxies={"http": proxy})
        end_time = time.time()

        # 检查响应是否成功
        if response.status_code == 200:
            download_time = end_time - start_time
            download_size = len(response.content)
            download_times.append(download_time)
            print(f"Download Size: {download_size / 1024 / 1024:.2f} MB")
            print(f"Download Time: {download_time:.2f} seconds")
        else:
            print("Failed to download the file")
            break

    # 计算平均带宽（单位：MB/秒）
    if download_times:
        average_time = sum(download_times) / len(download_times)
        download_speed = download_size / average_time / 1024 / 1024  # 单位转换为MB/秒
        print(f"Average Bandwidth: {download_speed:.2f} MB/s")


# 测试延迟和带宽
def measure_start(proxy):
    latency = measure_latency(proxy)
    if latency == -1:
        print("latency test timed out...no more load speed ")
        pass
    else:
        measure_bandwidth()


# 启动Xray 测试网络 以ping google为基准
def xray_start():
    result = subprocess.run(
        ["./xray_bin/xray > /dev/null 2>&1 &"],
        shell=True,
        stderr=subprocess.PIPE,
        cwd="./",
    )
    if result.stderr:
        print(result.stderr)
    else:
        print("xray service started...")

    # process = subprocess.Popen("./Xray/xray > /dev/null 2>&1 &", shell=True)
    #      process.kill()

    proxy = "http://127.0.0.1:10809"
    os.environ["http_proxy"] = proxy
    os.environ["https_proxy"] = proxy

    result = subprocess.run(
        ["curl www.google.com"],
        shell=True,
        stderr=subprocess.PIPE,
        cwd="./",
    )
    # 打印命令的输出
    # print(result.stdout)
    if result.stderr:
        print(result.stderr)
    print()

    # 测量延迟和带宽 以google为基准
    # measure_start(proxy)

    measure_latency(proxy)
    test_proxy_bandwidth(proxy)

    # 睡眠进程
    while True:
        print("sleeping...")
        time.sleep(10)
        pass


def decode_vmess(vmess_str):
    # 解码 base64 字符串
    vmess_bytes = base64.b64decode(vmess_str)
    # 将字节序列转换为字符串
    vmess_json = vmess_bytes.decode("utf-8")
    # 将 JSON 字符串解析为字典
    vmess_data = json.loads(vmess_json)
    return vmess_data


def generate_access_link(vmess_data):
    # 从字典中提取所需的信息
    host = vmess_data["add"]
    port = vmess_data["port"]
    id = vmess_data["id"]
    aid = vmess_data["aid"]
    path = vmess_data["path"]
    tls = vmess_data["tls"]
    net = vmess_data["net"]
    type = vmess_data["type"]
    # ps = vmess_data['ps']

    # 构建访问链接
    access_link = (
        f"vmess://{id}:{aid}@{host}:{port}/?path={path}&tls={tls}&net={net}&type={type}"
    )
    return access_link


if __name__ == "__main__":

    url = "https://moje.mojieurl.com/api/v1/client/subscribe?token=7b7c590e2dbd44a1e1aceb72c4e40d6f"
    proxy = "http://172.16.102.21:10809"

    encoded_content_url = ""  # get the results of http request

    try:
        response = requests.get(
            url, verify=False, timeout=20, proxies={"http": proxy, "https": proxy}
        )

        if response.status_code == 200:  # Status code 200 : http request successful...
            print("http request successful...")
            encoded_content_url = response.text
            # print("the results are as follows:")
            # print(encoded_content_url)
        else:
            print(f"Failed to retrieve the webpage: Status code {response.status_code}")
    except Timeout:
        print("http request timeout...")

    decoded_content_url = base64.b64decode(encoded_content_url)

    print("the first decoded results are as follows:")
    # print(decoded_content_url,type(decoded_content_url))

    str_decoded_content_url = decoded_content_url.decode("utf-8")
    # print(str_decoded_content_url,type(str_decoded_content_url))

    url_list = str_decoded_content_url.split("\n")
    for i in range(
        0, len(url_list) - 1
    ):  # vmess or trojan ,  the end of the split list is "\n"
        current_url = url_list[i]
        if "vmess" in current_url:
            vmess_str = current_url.split("://")[1]  # 输入 vmess 连接字符串
            vmess_data = decode_vmess(vmess_str)  # 解码 vmess 连接字符串
            access_link = generate_access_link(vmess_data)  # 生成访问链接
            print("ps:", vmess_data["ps"])
            print("the vmess url:", access_link)
        else:
            print("ps:", unquote(current_url.split("#")[1]))
            print("the trojan url:", current_url.split("#")[0])

    vmess_data = dict()

    url = "vmess://c3382d8a-2c92-4468-985b-87f4203b71b2:0@m.cnmjin.net:16648/?path=/&tls=&net=ws&type=none"
    url_dict = read_vmess(url)
    print(url_dict)
    the_total_dict = write_vmess_args(url_dict)
    config_path = "./xray_bin/config.json"
    write_config_json(the_total_dict, config_path)

    """
    测试修改config.json之后 xray 是否良好运行
    """
    xray_start()

    # 测量延迟和带宽 以google为基准
    # measure_start(proxy)
