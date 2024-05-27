import json
import requests
from requests.exceptions import Timeout
import base64
from urllib.parse import unquote
import subprocess
import time
import os
from prettytable import PrettyTable
import threading
import queue
from operator import itemgetter
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

total_url_list = list()  # Used to store information for all urls of the test results
q = (
    queue.Queue()
)  # FIFO quene that is used for threads to access information for all urls


# parse trojan url parameters, return url_trojan_dict
def read_trojan(url_trojan):
    url_trojan_dict = dict()
    url_trojan_dict["address"] = url_trojan.split("@")[1].split(":")[0]
    url_trojan_dict["port"] = int(url_trojan.split("@")[1].split(":")[1].split("?")[0])
    url_trojan_dict["password"] = url_trojan.split("@")[0].split("//")[1]
    return url_trojan_dict


# fill trojan parameters, return the_total_dict
def write_trojan_args(url_trojan_dict):
    the_total_dict = (
        dict()
    )  # The first dict element in the "outbounds" list in "config.json"
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


# parse vmess url parameters, return url_vmess_dict
def read_vmess(url_vmess):
    url_vmess_dict = dict()
    url_vmess_dict["address"] = url_vmess.split("@")[1].split(":")[0]
    url_vmess_dict["port"] = int(url_vmess.split("@")[1].split(":")[1].split("/")[0])
    url_vmess_dict["id"] = url_vmess.split("//")[1].split(":")[0]
    url_vmess_dict["alterId"] = int(url_vmess.split("@")[0].split(":")[2])
    url_vmess_dict["path"] = url_vmess.split("path=")[1].split("&")[0]
    return url_vmess_dict


# fill vmess parameters, return the_total_dict
def write_vmess_args(url_vmess_dict):
    the_total_dict = dict()
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


# update specified config for xray
def write_config_json(the_total_dict, config_path, port):
    # read json
    with open(config_path, "r") as f:
        data = json.load(f)

    # update data
    data["outbounds"][0] = the_total_dict
    data["inbounds"][0]["port"] = port - 1
    data["inbounds"][1]["port"] = port

    # write back
    with open(config_path, "w") as f:
        json.dump(
            data,
            f,
            indent=4,
        )


# test latency
def measure_latency(proxy, url):
    # create URL
    flag = False
    Time_connect = 0
    while flag == False and Time_connect < 3:
        Time_connect += 1
        try:
            start_time = time.time()
            response = requests.get(
                url,
                verify=False,
                timeout=8,
                proxies={"http": proxy, "https": proxy},
            )
            end_time = time.time()
            # test latency
            """ print("latency test started...") """
            if response.status_code == 200:
                # print the request content
                # print("response2 text:",response.text)
                flag = True
                # print latency
                """ print("latency:", int(response.elapsed.total_seconds() * 1000)) """
                # return int(response.elapsed.total_seconds() * 1000), Time_connect   # consider dns consume time
                return (
                    int((end_time - start_time) * 1000),
                    Time_connect,
                )  # not consider dns consume time
            else:
                """print(response.reason)
                print("Failed to request...retrying...")"""
                pass
        except:
            """print("latency test time out...")
            print("retries:", Time_connect)"""
        time.sleep(2)
    return -1, Time_connect


# test bandwidth
def test_proxy_bandwidth(proxy, url):
    url_list = [
        "https://github.com",
        "https://github.com",
    ]
    # k test times in order to calculate the average bandwidth
    k = 2
    download_times = []
    download_sizes = []
    download_speed = 0
    for i in range(0, k):
        flag = False
        Time_connect = 0
        while flag == False and Time_connect < 3:
            try:
                start_time = time.time()
                response = requests.get(
                    url_list[i],
                    verify=False,
                    timeout=10,
                    proxies={"http": proxy, "https": proxy},
                )
                end_time = time.time()

                if response.status_code == 200:
                    flag = True
                    download_time = end_time - start_time
                    download_sizes.append(len(response.content))
                    download_times.append(download_time)
                    break
                    """ print(f"Download Size: {download_size / 1024 / 1024:.2f} MB")
                    print(f"Download Time: {download_time:.2f} seconds") """
                else:
                    """print(response.reason)
                    print("Failed to request...retrying...")"""
                    pass
            except:
                """print("bandwidth test time out...")
                print("retries:", Time_connect)"""

            Time_connect += 1
            time.sleep(2)
        if Time_connect == 3 and flag == False:
            download_sizes.append(0)
            download_times.append(0)

    # calculate the average bandwidth（MB/s）
    if download_times:
        download_speed = (
            (download_sizes[1] - download_sizes[0])
            / (download_times[1] - download_times[0])
            / 1024
            / 1024
        )  # The unit is converted to MB/s
        # print(f"Average Bandwidth: {download_speed:.2f} MB/s")
        return download_speed


# test latency and bandwidth
def measure_start(port, url_for_test):
    proxy = "http://127.0.0.1:" + str(port)
    latency, time = measure_latency(proxy, url_for_test)
    bandwidth = 0
    """ if latency == -1:
        # print("latency test timed out...no more load speed ")
        pass
    else:
        bandwidth = test_proxy_bandwidth(proxy, url) """
    return latency, time, bandwidth


# start xray
def xray_start(xray_path, config_path):
    process = subprocess.Popen(
        "{} run -c {}> /dev/null 2>&1 &".format(xray_path, config_path), shell=True
    )
    if process.stderr:
        print(process.stderr)
    else:
        # print("xray service started...")
        pass
    # process.kill()

    return process


# decode vmess base64 strings
def decode_vmess(vmess_str):
    # decode base64 strings
    vmess_bytes = base64.b64decode(vmess_str)
    # converts a sequence of bytes to a string
    vmess_json = vmess_bytes.decode("utf-8")
    # parses a JSON string into a dict
    vmess_data = json.loads(vmess_json)
    return vmess_data


# generate the url link
def generate_access_link(vmess_data):
    # extract the required information from the dict
    host = vmess_data["add"]
    port = vmess_data["port"]
    id = vmess_data["id"]
    aid = vmess_data["aid"]
    path = vmess_data["path"]
    tls = vmess_data["tls"]
    net = vmess_data["net"]
    type = vmess_data["type"]
    # ps = vmess_data['ps']

    # generate the url link
    access_link = (
        f"vmess://{id}:{aid}@{host}:{port}/?path={path}&tls={tls}&net={net}&type={type}"
    )
    return access_link


# get score
def get_score(latency_proxy, time_proxy, bandwidth_proxy):
    k1 = 10000  # 100 * 100
    # k2 = 1500  # 50 * 30
    if latency_proxy == -1:
        return 0
    else:
        # return k1 / (latency_proxy * time_proxy) + k2 * bandwidth_proxy
        return k1 / (latency_proxy * time_proxy)


# print all the proxy test information
def print_prettytable(total_url_list):
    tb = PrettyTable()
    tb.field_names = [
        "Name",
        "Type",
        "Retries",
        "Latency(ms)",
        "Bandwidth(M/s)",
        "Score",
    ]
    for item in total_url_list:
        tb.add_row(
            [
                item["name"],
                item["type"],
                item["time"],
                item["latency"],
                "---",  # item["bandwidth"]
                "{:.2f}".format(item["score"]),
            ]
        )
    tb.align = "c"  # align : l c r
    print(tb)


# thread exc
def quene_thread_exc(thread_id, thread_path, port, url_for_test):
    while not q.empty():
        item = q.get()  # take a url to test
        url = item["url"]

        the_total_dict = dict()
        if item["type"] == "vmess":
            url_dict = read_vmess(url)
            # print(url_dict)
            the_total_dict = write_vmess_args(url_dict)
        else:
            url_dict = read_trojan(url)
            # print(url_dict)
            the_total_dict = write_trojan_args(url_dict)

        xray_path = "./xray_bin/xray"
        config_path = thread_path + "config{}.json".format(thread_id)
        write_config_json(the_total_dict, config_path, port)
        process = xray_start(xray_path, config_path)

        latency_proxy, time_proxy, bandwidth_proxy = measure_start(port, url_for_test)
        item["latency"] = latency_proxy
        item["time"] = time_proxy
        item["bandwidth"] = bandwidth_proxy
        item["score"] = get_score(latency_proxy, time_proxy, bandwidth_proxy)

        process.kill()
        total_url_list.append(item)
    # time.sleep(2)


if __name__ == "__main__":
    py_config_path = "./config/py_config.json"
    url_proxies = ""  # random Initial value
    time_exc_sleep = 10000  # random Initial value
    time_request_sleep = 10  # random Initial value
    json_data = None
    time_check_net_well = 100
    try:
        # read json
        with open(py_config_path, "r") as f:
            json_data = json.load(f)

            # read data from json
            url_proxies = json_data["url"]
            time_exc_sleep = json_data["exc_sleep_time"]
            time_request_sleep = json_data["request_sleep_time"]
            time_check_net_well = json_data["check_net_well_time"]
            print(
                "the following paramters come from your mkdir [{}]:".format(
                    py_config_path
                )
            )
            tb = PrettyTable()
            tb.field_names = [
                "request_sleep_time(h)",
                "proxy_test_sleep_time(h)",
                "check_net_well_time(h)",
            ]
            tb.add_row(
                [
                    "{:.4f}".format(time_request_sleep / 3600),
                    "{:.4f}".format(time_exc_sleep / 3600),
                    "{:.4f}".format(time_check_net_well / 3600),
                ]
            )
            tb.align = "c"  # align : l c r
            print(tb)
            tb1 = PrettyTable()
            tb1.field_names = [
                "help_proxy",
                "host_port",
            ]
            tb1.add_row(
                [
                    json_data["help_proxy"],
                    json_data["host_port"],
                ]
            )
            tb1.align = "c"  # align : l c r
            print(tb1)
            print(
                "you can customize above parameters by manually modifying the json file..."
            )
    except:
        data = {
            "url": "https://example.com",
            "exc_sleep_time": 36000,
            "check_net_well_time": 3600,
            "host_port": 10809,
            "request_sleep_time": 1800,
            "help_proxy": "http://example.com:10809",
        }
        with open(py_config_path, "w") as f:
            json.dump(
                data,
                f,
                indent=4,
            )
        print(
            "{} should be not null... \n Please fill in the url and sleep time parameters".format(
                py_config_path
            )
        )
        exit()

    xray_path = "./xray_bin/xray"
    config_path = "./config/default_config.json"  # here you can use your config.json for first xray start ，
    process0 = xray_start(xray_path, config_path)
    os.environ["http_proxy"] = "http://127.0.0.1:10809"
    os.environ["https_proxy"] = "http://127.0.0.1:10809"

    while True:
        total_url_list.clear()  # reset
        proxy = "http://127.0.0.1:10809"
        # url_proxies = "https://moje.mojieurl.com/api/v1/client/subscribe?token=7b7c590e2dbd44a1e1aceb72c4e40d6f"
        # inner_proxy = "http://172.16.102.21:10809"
        print("the proxy test service started...")
        print("getting the results of http request for urls...")
        encoded_content_url = ""  # get the results of http request
        flag = False
        reconnect_times = 0
        while flag == False:
            reconnect_times += 1
            if (
                reconnect_times % 10 == 0
            ):  # if the current xray proxy is not working well, you can use a user-defined proxy every 10 times
                if "help_proxy" in json_data:
                    proxy = json_data["help_proxy"]  # your proxy
                else:
                    proxy = "http://127.0.0.1:" + str(json_data["host_port"])
            else:
                proxy = "http://127.0.0.1:" + str(json_data["host_port"])
            try:
                response = requests.get(
                    url_proxies,
                    verify=False,
                    timeout=20,
                    proxies={"http": proxy, "https": proxy},
                )

                if (
                    response.status_code == 200
                ):  # Status code 200 : http request successful...
                    print("get http request successful...")
                    flag = True
                    encoded_content_url = response.text
                    # print("the results are as follows:")
                    # print(encoded_content_url)
                else:
                    print(
                        f"Failed to retrieve the webpage: Status code {response.status_code}"
                    )
            except:
                print("http request timeout...retrying...")
                time.sleep(1)
                if reconnect_times % 10 == 0:
                    reconnect_times = 0
                    time.sleep(time_request_sleep)

        decoded_content_url = base64.b64decode(encoded_content_url)

        # print("the first decoded urls are as follows:")
        # print(decoded_content_url, type(decoded_content_url))

        str_decoded_content_url = decoded_content_url.decode("utf-8")
        # print(str_decoded_content_url,type(str_decoded_content_url))

        url_list = str_decoded_content_url.split("\n")
        for thread_id in range(
            0, len(url_list) - 1
        ):  # vmess or trojan ,  the end of the split list is "\n"
            current_url = url_list[thread_id]
            if "vmess" in current_url:
                vmess_str = current_url.split("://")[1]
                vmess_data = decode_vmess(vmess_str)
                access_link = generate_access_link(vmess_data)
                single_url_dict1 = dict()
                single_url_dict1["name"] = vmess_data["ps"]
                single_url_dict1["url"] = access_link
                single_url_dict1["type"] = "vmess"
                single_url_dict1["latency"] = -1
                single_url_dict1["time"] = -1
                single_url_dict1["bandwidth"] = -1
                single_url_dict1["score"] = -1
                # total_url_list.append(single_url_dict1)
                q.put(single_url_dict1)
            else:
                single_url_dict2 = dict()
                single_url_dict2["name"] = unquote(
                    current_url.split("#")[1].split("\r")[0]
                )
                single_url_dict2["url"] = current_url.split("#")[0]
                single_url_dict2["type"] = "trojan"
                single_url_dict2["latency"] = -1
                single_url_dict2["time"] = -1
                single_url_dict2["bandwidth"] = -1
                single_url_dict2["score"] = -1
                # total_url_list.append(single_url_dict2)
                q.put(single_url_dict2)

        num_urls = q.qsize()
        print("the url number is as follows:")
        print(num_urls)

        print("proxy test started...")

        url_for_test = "https://www.google.com"

        # create threads list
        threads = []
        thread_num = 9
        # create threads and start
        start_port = 60010
        for thread_id in range(1, thread_num + 1):
            thread_path = "./xray_bin/thread_config/"
            port = start_port + thread_id * 2
            t = threading.Thread(
                target=quene_thread_exc,
                args=(thread_id, thread_path, port, url_for_test),
            )
            threads.append(t)
            t.start()
            print("thread_{} port:{} started...".format(thread_id, port))

        # waiting for all threads to complete
        for t in threads:
            t.join()

        # print the proxy test results
        print("the proxy test results are as follows:")
        print_prettytable(total_url_list)

        temp = {
            "name": "null",
            "type": "null",
            "time": 0,
            "latency": 0,
            "bandwidth": "---",
            "score": 0,
            "url": "null",
        }
        for item in total_url_list:
            if temp["score"] < item["score"]:
                temp["name"] = item["name"]
                temp["type"] = item["type"]
                temp["url"] = item["url"]
                temp["time"] = item["time"]
                temp["latency"] = item["latency"]
                temp["bandwidth"] = item["bandwidth"]
                temp["score"] = item["score"]

        print("the selected url information is as follows:")
        temp_list = list()
        temp_list.append(temp)
        print_prettytable(temp_list)

        print("changing the proxy node... ")

        the_selected_dict = dict()
        if temp["type"] == "vmess":
            url_dict = read_vmess(temp["url"])
            the_selected_dict = write_vmess_args(url_dict)
        else:
            url_dict = read_trojan(temp["url"])
            the_selected_dict = write_trojan_args(url_dict)

        # determines whether the selected proxy is the current proxy
        # read json
        flag_same_proxy = False
        with open(config_path, "r") as f:
            data = json.load(f)
            type_data = data["outbounds"][0]["protocol"]
            settings_data = data["outbounds"][0]["settings"]
            if type_data == temp["type"]:
                address_data = ""
                port_data = ""
                if type_data == "vmess":
                    address_data = settings_data["vnext"][0]["address"]
                    port_data = str(settings_data["vnext"][0]["port"])
                else:  # trojan url
                    address_data = settings_data["servers"][0]["address"]
                    port_data = str(settings_data["servers"][0]["port"])
                if address_data in temp["url"] and port_data in temp["url"]:
                    flag_same_proxy = True
            else:
                address_data = ""
                port_data = ""
                if type_data == "vmess":
                    address_data = settings_data["vnext"][0]["address"]
                    port_data = str(settings_data["vnext"][0]["port"])
                else:  # trojan url
                    address_data = settings_data["servers"][0]["address"]
                    port_data = str(settings_data["servers"][0]["port"])
                print("the current address:{} port:{}".format(address_data, port_data))
                print("the next proxy url:{}".format(temp["url"]))
        if (
            flag_same_proxy
        ):  # determines whether the selected proxy is the current proxy
            print(
                "The current proxy is already the best and does not need to be replaced..."
            )
        else:
            print("changing the proxy...trying restart xray...")
            process0.kill()
            xray_path = "./xray_bin/xray"
            config_path = "./xray_bin/config.json"
            write_config_json(the_selected_dict, config_path, 10809)
            write_config_json(the_selected_dict, "./config/default_config.json", 10809)
            process0 = xray_start(xray_path, config_path)
            if process0.stderr:
                print(process0.stderr)
                print("Please restart manually...")
                exit()
            else:
                print("xray service restarted successfully...")

        # the proxy test service sleeping
        print("the proxy test service is sleeping...")
        print(
            "The next proxy node replacement will take place {:.4f} hours later...".format(
                time_exc_sleep / 3600
            )
        )

        # check net work well or not

        sorted_url_list = sorted(total_url_list, key=itemgetter("score"), reverse=True)
        # print_prettytable(sorted_url_list)
        """  {
            "name": "",
            "url": "vmess://",
            "type": "vmess",
            "latency": ,
            "time": ,
            "bandwidth": 0,
            "score": 13.054867,
        } """

        print(proxy)
        check_error = 0
        available_url_id = 1
        for i in range(
            int((time_exc_sleep + time_check_net_well - 1) / time_check_net_well)
        ):
            flag_check_net = False
            for _ in range(10):
                try:
                    response = requests.get(
                        url_proxies,
                        verify=False,
                        timeout=20,
                        proxies={"http": proxy, "https": proxy},
                    )
                    if response.status_code == 200:
                        print("Times:{}  check net well...".format(i + 1))
                        flag_check_net = True
                        check_error = 0
                        break
                        # encoded_content_url = response.text
                    else:
                        print(
                            f"Failed to retrieve the webpage: Status code {response.status_code}"
                        )
                except:
                    # net work not well, recheck
                    time.sleep(1)

            if flag_check_net == False:
                print("Times:{}  check net not well...warning...".format(i + 1))
                check_error += 1
            if check_error == 3:  #
                check_error = 0  # reset
                print("the currnt proxy work not well, need update...")
                process0.kill()
                url_dict_temp = sorted_url_list[available_url_id]
                available_url_id = (available_url_id + 1) % num_urls
                the_selected_dict1 = {}
                if url_dict_temp["type"] == "vmess":
                    url_dict = read_vmess(url_dict_temp["url"])
                    the_selected_dict1 = write_vmess_args(url_dict)
                else:
                    url_dict = read_trojan(url_dict_temp["url"])
                    the_selected_dict1 = write_trojan_args(url_dict)
                xray_path = "./xray_bin/xray"
                config_path = "./xray_bin/config.json"
                write_config_json(the_selected_dict1, config_path, 10809)
                write_config_json(
                    the_selected_dict1, "./config/default_config.json", 10809
                )
                process0 = xray_start(xray_path, config_path)
                print("proxy update finished...")

                print("the current proxy is as follows:")
                url_dict_temp_list = list()
                url_dict_temp_list.append(url_dict_temp)
                print_prettytable(url_dict_temp_list)

                if process0.stderr:
                    print(process0.stderr)
                    print("Please restart manually...")
                    exit()
                else:
                    print("xray service restarted successfully...")

            time.sleep(time_check_net_well)
