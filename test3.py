import time
import requests
import socks
import socket
from urllib.parse import urlparse
import http.client


def get_http_timings_with_proxy(url, proxy_url=None):
    parsed_url = urlparse(url)
    timings = {}
    if proxy_url:
        parsed_proxy_url = urlparse(proxy_url)

        # 设置代理
        socks_proxy_type = (
            socks.PROXY_TYPE_HTTP
            if parsed_proxy_url.scheme == "http"
            else socks.PROXY_TYPE_SOCKS5
        )
        socks.set_default_proxy(
            socks_proxy_type, parsed_proxy_url.hostname, parsed_proxy_url.port
        )
    socket.socket = socks.socksocket

    # 创建连接对象
    conn = (
        http.client.HTTPSConnection(parsed_url.netloc)
        if parsed_url.scheme == "https"
        else http.client.HTTPConnection(parsed_url.netloc)
    )

    try:
        # DNS 解析时间
        timings["start_dns"] = time.time()
        conn.connect()
        timings["end_dns"] = time.time()

        # TCP 连接时间
        timings["start_tcp"] = timings["end_dns"]
        conn.sock.settimeout(10)
        conn.request("GET", parsed_url.path or "/")
        timings["end_tcp"] = time.time()

        # 发送请求时间
        timings["start_tls"] = timings["end_tcp"]
        response = conn.getresponse()
        timings["end_tls"] = time.time()

        # 服务器响应时间
        timings["start_server"] = timings["end_tls"]
        size = 0
        while True:
            chunk = response.read()
            if chunk:
                size += len(chunk)
            else:
                break
        timings["end_server"] = time.time()
        print("data-size(KB):", size / 1024)

    finally:
        conn.close()

    # 计算各阶段时间
    dns_time = timings["end_dns"] - timings["start_dns"]
    tcp_time = timings["end_tcp"] - timings["start_tcp"]
    tls_time = timings["end_tls"] - timings["start_tls"]
    server_time = timings["end_server"] - timings["start_server"]
    total_time = timings["end_server"] - timings["start_dns"]

    print(f"DNS Lookup Time: {dns_time:.4f} seconds")
    print(f"TCP Connection Time: {tcp_time:.4f} seconds")
    print(f"TLS Handshake Time: {tls_time:.4f} seconds")
    print(f"Server Processing Time: {server_time:.4f} seconds")
    print(f"Total Time: {total_time:.4f} seconds")


# 基于Ubuntu 20.04 容器部署，编写dockerfile，构建镜像

# 测试 URL 和代理
url = "https://www.baidu.com"
# proxy_url = "http://127.0.0.1:10809"
proxy_url = None

get_http_timings_with_proxy(url, proxy_url)
