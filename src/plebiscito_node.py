"""
This module impelments the behavior of a node
"""

from queue import Empty
import random
import threading
import time
from src.config import Utility
from src.network import Endpoint
from datetime import datetime, timedelta
import copy
import logging
import queue
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

TRACE = 5

class InternalError(Exception):
    "Raised when the input value is less than 18"
    pass

bids = None
bids_lock = None
q = None

class PNode:
    class MyHandler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            return
        
        def do_POST(self):
            global q
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length).decode("utf-8")
            q.put(json.loads(post_data))

            # Send an HTTP response
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

        def do_GET(self):
            global bids, bids_lock
            if self.path == "/":
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
            elif self.path == "/status":
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
            elif self.path.startswith("/transaction"):
                with bids_lock:
                    if len(self.path.split("/")) != 2:
                        transaction_id = self.path.split("/")[-1]
                        if transaction_id in bids:
                            self.send_response(200)
                            self.send_header("Content-type", "text/html")
                            self.end_headers()
                            self.wfile.write(str(bids[transaction_id]["auction_id"]).encode("utf-8"))
                        else:
                            self.send_response(404)
                            self.send_header("Content-type", "text/html")
                            self.end_headers()
                            self.wfile.write(f"Transaction not avaiable".encode("utf-8"))
                    else:
                        ret = ""
                        for k in bids:
                            ret += f"Transaction ID ({k}) &emsp; winner(s): {bids[k]['auction_id']} &emsp; bid(s): {bids[k]['bid']}<br>"
                        self.send_response(200)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
                        self.wfile.write(ret.encode("utf-8"))
                
            else:
                self.send_response(404)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"Resource not found")

    def __init__(self, id, utility=Utility.LGF, self_endpoint=Endpoint("e", "localhost", "9191"), neighbors_endpoint=[], enable_logging=False, reduce_packets=False, timeout=0.05):
        global bids, bids_lock, q

        self.__id = id  # unique edge node id
        self.__utility = utility
        self.__enable_logging = enable_logging
        self.__neighbors_endpoint = neighbors_endpoint
        self.__active_endpoints = {}
        self.__self_endpoint = self_endpoint
        self.__reduce_packets = reduce_packets
        self.__timeout = timeout

        q = queue.Queue()

        # TODO: update the initial values
        self.__initial_bw = 3000
        self.__initial_cpu = 3000
        self.__initial_gpu = 3000
        self.__initial_memory = 3000
        self.__updated_bw = self.__initial_bw
        self.__updated_gpu = self.__initial_gpu
        self.__updated_cpu = self.__initial_cpu
        self.__updated_memory = self.__initial_memory

        self.__counter = {}
        self.__item = {}
        bids_lock = threading.Lock()
        bids = {}
        self.__layer_bid_already = {}
        self.__tasks_from_clients = []

        self.__run_http_server()

    def get_avail_gpu(self):
        return self.__updated_gpu

    def get_avail_cpu(self):
        return self.__updated_cpu

    def get_avail_bw(self):
        return self.__updated_gpu

    def get_avail_memory(self):
        return self.__updated_memory

    def get_available_resources(self):
        return (self.__updated_cpu, self.__updated_gpu, self.__updated_memory, self.__updated_bw)

    def __run_http_server(self):
        if self.__self_endpoint is None:
            server_address = ("", 8000)  # Listen on all interfaces, port 8000
        else:
            server_address = (self.__self_endpoint.get_IP(), self.__self_endpoint.get_port())

        # Pass the shared queue to the HTTP server
        self.__httpd = HTTPServer(server_address, PNode.MyHandler)
        threading.Thread(target=self.__httpd.serve_forever).start()

    def __init_null(self):
        global bids, bids_lock

        #print(f"First message for transaction {self.__item['job_id']}")
        if self.__item["job_id"] not in self.__active_endpoints:
            self.__active_endpoints[self.__item["job_id"]] = []
            for e in self.__neighbors_endpoint:
                if e.is_active():
                    self.__active_endpoints[self.__item["job_id"]].append(e)

        with bids_lock:
            bids[self.__item["job_id"]] = {
                "job_id": self.__item["job_id"],
                "user": int(),
                "auction_id": list(),
                "Bundle_gpus": self.__item["Bundle_gpus"],
                "Bundle_cpus": self.__item["Bundle_cpus"],
                "Bundle_memory": self.__item["Bundle_memory"],
                "Bundle_bw": self.__item["Bundle_bw"],
                "bid": list(),
                "timestamp": list(),
                "arrival_time": datetime.timestamp(datetime.now()),
                "Bundle_min": self.__item["Bundle_min"],
                "Bundle_max": self.__item["Bundle_max"],
                "edge_id": self.__id,
                "Bundle_size": self.__item["Bundle_size"],
                "bid": [float("-inf") for _ in range(self.__item["Bundle_size"])],
                "auction_id": [float("-inf") for _ in range(self.__item["Bundle_size"])],
                "timestamp": [datetime.timestamp(datetime.now() - timedelta(days=1)) for _ in range(self.__item["Bundle_size"])],
            }

        self.__layer_bid_already[self.__item["job_id"]] = [False] * self.__item["Bundle_size"]

    def __utility_function(self, avail_bw, avail_cpu, avail_gpu):
        if self.__utility == Utility.LGF:
            return avail_gpu
        
    def __invalidate_bid(self, msg):
        global bids, bids_lock
        
        with bids_lock:
            new_bid = [1000000000 for _ in range(self.__item["Bundle_size"])]
            new_auction = [-1000000000 for _ in range(self.__item["Bundle_size"])]
            new_timestamp = [datetime.timestamp(datetime.now() + timedelta(weeks=25)) for _ in range(self.__item["Bundle_size"])]
            
            bids[self.__item["job_id"]]["bid"] = new_bid
            bids[self.__item["job_id"]]["auction_id"] = new_auction
            bids[self.__item["job_id"]]["timestamp"] = new_timestamp

            msg["bid"] = new_bid
            msg["auction_id"] = new_auction
            msg["timestamp"] = new_timestamp

            for e in self.__active_endpoints[self.__item["job_id"]]:
                _ = e.send_msg(msg)


    def __forward_to_neighbohors(self, custom_dict=None, resend_bid=False, first_msg=False):
        global bids, bids_lock

        msg = {
            "type": self.__item["type"],
            "job_id": self.__item["job_id"],
            "user": self.__item["user"],
            "edge_id": self.__id,
            "Bundle_gpus": self.__item["Bundle_gpus"],
            "Bundle_cpus": self.__item["Bundle_cpus"],
            "Bundle_memory": self.__item["Bundle_memory"],
            "Bundle_bw": self.__item["Bundle_bw"],
            "Bundle_size": self.__item["Bundle_size"],
            "Bundle_min": self.__item["Bundle_min"],
            "Bundle_max": self.__item["Bundle_max"],
        }

        if first_msg:
            for e in self.__active_endpoints[self.__item["job_id"]]:
                _ = e.send_msg(msg)
            return

        if custom_dict == None and not resend_bid:
            with bids_lock:
                msg["auction_id"] = copy.deepcopy(bids[self.__item["job_id"]]["auction_id"])
                msg["bid"] = copy.deepcopy(bids[self.__item["job_id"]]["bid"])
                msg["timestamp"] = copy.deepcopy(bids[self.__item["job_id"]]["timestamp"])
        elif custom_dict != None and not resend_bid:
            msg["auction_id"] = copy.deepcopy(custom_dict["auction_id"])
            msg["bid"] = copy.deepcopy(custom_dict["bid"])
            msg["timestamp"] = copy.deepcopy(custom_dict["timestamp"])
        elif resend_bid:
            if "auction_id" in self.__item:
                msg["auction_id"] = copy.deepcopy(self.__item["auction_id"])
                msg["bid"] = copy.deepcopy(self.__item["bid"])
                msg["timestamp"] = copy.deepcopy(self.__item["timestamp"])
            # msg['edge_id'] = self.__item['edge_id']

        if self.__enable_logging:
            self.print_node_state("FORWARD", True)
        
        for e in self.__active_endpoints[self.__item["job_id"]]:
            success = e.send_msg(msg)
            if not success:
                self.__invalidate_bid(msg)
                break

        return

    def print_node_state(self, msg, bid=False, type="debug"):
        logger_method = getattr(logging, type)
        # print(str(self.__item.get('auction_id')) if bid and self.__item.get('auction_id') is not None else "\n")
        logger_method(str(msg) + " job_id:" + str(self.__item["job_id"]) + " NODEID:" + str(self.__id) + " from_edge:" + str(self.__item["edge_id"]) + " initial GPU:" + str(self.__initial_gpu) + " available GPU:" + str(self.__updated_gpu) + " initial CPU:" + str(self.__initial_cpu) + " available CPU:" + str(self.__updated_cpu))

    def __update_local_val(self, tmp, index, id, bid, timestamp):
        tmp["job_id"] = self.__item["job_id"]
        tmp["auction_id"][index] = id
        tmp["bid"][index] = bid
        tmp["timestamp"][index] = timestamp
        return index + 1

    def reset(self, index, dict, bid_time):
        dict["auction_id"][index] = float("-inf")
        dict["bid"][index] = float("-inf")
        dict["timestamp"][index] = bid_time  # - timedelta(days=1)
        return index + 1

    # NOTE: inprove in future iterations
    def compute_layer_score(self, cpu, gpu, bw):
        return gpu

    def __bid_topology(self):
        pass

    def __can_host(self, i, diff_cpu=0, diff_gpu=0, diff_bw=0, diff_memory=0):
        if (not self.__layer_bid_already[self.__item["job_id"]][i] and
                self.__item["Bundle_gpus"][i] <= self.__updated_gpu - diff_gpu and 
                self.__item["Bundle_cpus"][i] <= self.__updated_cpu - diff_cpu and 
                self.__item["Bundle_bw"][i] <= self.__updated_bw - diff_bw and
                self.__item["Bundle_memory"][i] <= self.__updated_memory - diff_memory): 
            return True
        return False

    def __bid(self):
        global bids, bids_lock
        with bids_lock:
            tmp_bid = copy.deepcopy(bids[self.__item["job_id"]])

        bidtime = datetime.timestamp(datetime.now())

        possible_layer = []

        if self.__id not in tmp_bid["auction_id"]:
            for i in range(len(self.__layer_bid_already[self.__item["job_id"]])):
                if self.__can_host(i):
                    possible_layer.append(i)
        else:
            return False

        while len(possible_layer) > 0:
            best_placement = None
            best_score = None

            for l in possible_layer:
                score = self.compute_layer_score(
                    self.__item["Bundle_cpus"][l],
                    self.__item["Bundle_gpus"][l],
                    self.__item["Bundle_bw"][l],
                )
                if best_score == None or score > best_score:
                    best_score = score
                    best_placement = l

            bid = self.__utility_function(self.__updated_bw, self.__updated_cpu, self.__updated_gpu)
            self.__layer_bid_already[self.__item["job_id"]][best_placement] = True
            possible_layer.remove(best_placement)

            if bid > tmp_bid["bid"][best_placement] or (bid == tmp_bid["bid"][best_placement] and self.__id < tmp_bid["auction_id"][best_placement]):
                gpu_ = self.__item["Bundle_gpus"][best_placement]
                cpu_ = self.__item["Bundle_cpus"][best_placement]
                bw_ = self.__item["Bundle_bw"][best_placement]
                mem_ = self.__item["Bundle_memory"][best_placement]

                Bundle_size = 1

                layers = []

                tmp_bid["bid"][best_placement] = bid
                tmp_bid["auction_id"][best_placement] = self.__id
                tmp_bid["timestamp"][best_placement] = bidtime

                left_bound = best_placement
                right_bound = best_placement

                success = False

                while True:
                    if Bundle_size == self.__item["Bundle_max"]:
                        success = True
                        break

                    left_bound = left_bound - 1
                    right_bound = right_bound + 1

                    left_score = None
                    right_score = None

                    if (left_bound >= 0 and self.__can_host(left_bound, cpu_, gpu_, bw_, mem_)):
                        left_score = self.compute_layer_score(
                            self.__item["Bundle_cpus"][left_bound],
                            self.__item["Bundle_gpus"][left_bound],
                            self.__item["Bundle_bw"][left_bound],
                        )

                    if (right_bound < len(self.__item["Bundle_cpus"]) and self.__can_host(right_bound, cpu_, gpu_, bw_, mem_)):
                        right_score = self.compute_layer_score(
                            self.__item["Bundle_cpus"][right_bound],
                            self.__item["Bundle_gpus"][right_bound],
                            self.__item["Bundle_bw"][right_bound],
                        )

                    target_layer = None

                    if (left_score is not None and right_score is None) or (left_score is not None and right_score is not None and left_score >= right_score):
                        target_layer = left_bound
                        right_bound -= 1

                    if (right_score is not None and left_score is None) or (left_score is not None and right_score is not None and left_score < right_score):
                        target_layer = right_bound
                        left_bound += 1

                    if target_layer is not None:
                        bid = self.__utility_function(
                            self.__updated_bw, self.__updated_cpu, self.__updated_gpu
                        )

                        if bid > tmp_bid["bid"][target_layer] or (bid == tmp_bid["bid"][target_layer] and self.__id < tmp_bid["auction_id"][target_layer]):
                            tmp_bid["bid"][target_layer] = bid
                            tmp_bid["auction_id"][target_layer] = self.__id
                            tmp_bid["timestamp"][target_layer] = bidtime

                            Bundle_size += 1
                            layers.append(target_layer)

                            cpu_ += self.__item["Bundle_cpus"][target_layer]
                            gpu_ += self.__item["Bundle_gpus"][target_layer]
                            bw_ += self.__item["Bundle_bw"][target_layer]
                            mem_ += self.__item["Bundle_memory"][target_layer]
                        else:  # try also on the other side
                            found = False

                            # we tried on the left bound, let's try on the right one now
                            if target_layer == left_bound and right_score is not None:
                                target_layer = right_bound + 1
                                found = True

                            # we tried on the right bound, let's try on the left one now
                            if target_layer == right_bound and left_score is not None:
                                target_layer = left_bound - 1
                                found = True

                            if found:
                                bid = self.__utility_function(
                                    self.__updated_bw,
                                    self.__updated_cpu,
                                    self.__updated_gpu,
                                )
                                bid -= self.__id * 0.000000001

                                # if my bid is higher than the current bid, I can bid on the layer
                                if bid > tmp_bid["bid"][target_layer] or (bid == tmp_bid["bid"][target_layer] and self.__id < tmp_bid["auction_id"][target_layer]):
                                    tmp_bid["bid"][target_layer] = bid
                                    tmp_bid["auction_id"][target_layer] = self.__id
                                    tmp_bid["timestamp"][target_layer] = bidtime

                                    Bundle_size += 1
                                    layers.append(target_layer)

                                    cpu_ += self.__item["Bundle_cpus"][target_layer]
                                    gpu_ += self.__item["Bundle_gpus"][target_layer]
                                    bw_ += self.__item["Bundle_bw"][target_layer]
                                    mem_ += self.__item["Bundle_memory"][target_layer]
                                    # bw_ += self.__item['NN_data_size'][target_layer]
                                else:
                                    if (Bundle_size >= self.__item["Bundle_min"] and Bundle_size <= self.__item["Bundle_max"]):
                                        success = True
                                    break
                            else:
                                if (Bundle_size >= self.__item["Bundle_min"] and Bundle_size <= self.__item["Bundle_max"]):
                                    success = True
                                break
                    else:
                        if Bundle_size >= self.__item["Bundle_min"] and Bundle_size <= self.__item["Bundle_max"]:
                            success = True
                        break

                if success:
                    self.__updated_cpu -= cpu_
                    self.__updated_gpu -= gpu_
                    self.__updated_bw -= bw_
                    self.__updated_memory -= mem_

                    with bids_lock:
                        bids[self.__item["job_id"]] = copy.deepcopy(tmp_bid)

                    for l in layers:
                        self.__layer_bid_already[self.__item["job_id"]][l] = True

                    return True

        return False

    def __deconfliction(self):
        global bids, bids_lock
        rebroadcast = False
        k = self.__item["edge_id"]  # sender
        i = self.__id  # receiver

        with bids_lock:
            tmp_local = copy.deepcopy(bids[self.__item["job_id"]])
            prev_bet = copy.deepcopy(bids[self.__item["job_id"]])
        
        index = 0
        reset_flag = False
        reset_ids = []
        bid_time = datetime.timestamp(datetime.now())

        while index < self.__item["Bundle_size"]:
            z_kj = self.__item["auction_id"][index]
            z_ij = tmp_local["auction_id"][index]
            y_kj = self.__item["bid"][index]
            y_ij = tmp_local["bid"][index]
            t_kj = self.__item["timestamp"][index]
            t_ij = tmp_local["timestamp"][index]

            if self.__enable_logging:
                logger_method = getattr(logging, "debug")
                logger_method(
                    "DECONFLICTION - NODEID(i):"
                    + str(i)
                    + " sender(k):"
                    + str(k)
                    + " z_kj:"
                    + str(z_kj)
                    + " z_ij:"
                    + str(z_ij)
                    + " y_kj:"
                    + str(y_kj)
                    + " y_ij:"
                    + str(y_ij)
                    + " t_kj:"
                    + str(t_kj)
                    + " t_ij:"
                    + str(t_ij)
                )

            if z_kj == k:
                if z_ij == i:
                    if y_kj > y_ij:
                        rebroadcast = True
                        if self.__enable_logging:
                            logging.log(TRACE, "NODEID:" +
                                        str(self.__id) + " #1")
                        index = self.__update_local_val(
                            tmp_local,
                            index,
                            z_kj,
                            y_kj,
                            t_kj
                        )

                    elif y_kj == y_ij and z_kj < z_ij:
                        if self.__enable_logging:
                            logging.log(TRACE, "NODEID:" +
                                        str(self.__id) + " #3")
                        rebroadcast = True
                        index = self.__update_local_val(
                            tmp_local,
                            index,
                            z_kj,
                            y_kj,
                            t_kj,
                        )

                    else:
                        rebroadcast = True
                        if self.__enable_logging:
                            logging.log(TRACE, "NODEID:" +
                                        str(self.__id) + " #2")
                        index = self.__update_local_val(
                            tmp_local,
                            index,
                            z_ij,
                            tmp_local["bid"][index],
                            bid_time,
                        )

                elif z_ij == k:
                    if t_kj > t_ij:
                        if self.__enable_logging:
                            logging.log(TRACE, "NODEID:" +
                                        str(self.__id) + "#4")
                        index = self.__update_local_val(
                            tmp_local,
                            index,
                            z_kj,
                            y_kj,
                            t_kj,
                        )
                        rebroadcast = True
                    else:
                        if self.__enable_logging:
                            logging.log(TRACE, "NODEID:" +
                                        str(self.__id) + " #5 - 6")
                        index += 1

                elif z_ij == float("-inf"):
                    if self.__enable_logging:
                        logging.log(TRACE, "NODEID:" + str(self.__id) + " #12")
                    index = self.__update_local_val(
                        tmp_local,
                        index,
                        z_kj,
                        y_kj,
                        t_kj,
                    )
                    rebroadcast = True

                elif z_ij != i and z_ij != k:
                    if y_kj >= y_ij and t_kj >= t_ij:
                        if self.__enable_logging:
                            logging.log(TRACE, "NODEID:" +
                                        str(self.__id) + " #7")
                        index = self.__update_local_val(
                            tmp_local,
                            index,
                            z_kj,
                            y_kj,
                            t_kj,
                        )
                        rebroadcast = True
                    elif y_kj < y_ij and t_kj < t_ij:
                        if self.__enable_logging:
                            logging.log(TRACE, "NODEID:" +
                                        str(self.__id) + " #8")
                        index += 1
                        rebroadcast = True
                    elif y_kj == y_ij:
                        if self.__enable_logging:
                            logging.log(TRACE, "NODEID:" +
                                        str(self.__id) + " #9")
                        rebroadcast = True
                        index += 1
                    elif y_kj < y_ij and t_kj >= t_ij:
                        if self.__enable_logging:
                            logging.log(TRACE, "NODEID:" +
                                        str(self.__id) + " #10reset")
                        index += 1
                        rebroadcast = True
                    elif y_kj > y_ij and t_kj < t_ij:
                        if self.__enable_logging:
                            logging.log(TRACE, "NODEID:" +
                                        str(self.__id) + " #11rest")
                        index = self.__update_local_val(
                            tmp_local,
                            index,
                            z_kj,
                            y_kj,
                            t_kj,
                        )
                        rebroadcast = True
                    else:
                        if self.__enable_logging:
                            logging.log(TRACE, "NODEID:" +
                                        str(self.__id) + " #11else")
                        index += 1
                        rebroadcast = True
                else:
                    index += 1
                    if self.__enable_logging:
                        logging.log(TRACE, "eccoci")

            elif z_kj == i:
                if z_ij == i:
                    if t_kj > t_ij:
                        if self.__enable_logging:
                            logging.log(
                                TRACE, "NODEID:" +
                                str(self.__id) + " #13Flavio"
                            )
                        index = self.__update_local_val(
                            tmp_local,
                            index,
                            z_kj,
                            y_kj,
                            t_kj,
                        )
                        rebroadcast = True
                    else:
                        if self.__enable_logging:
                            logging.log(
                                TRACE, "NODEID:" +
                                str(self.__id) + " #13elseFlavio"
                            )
                        index += 1

                elif z_ij == k:
                    if self.__enable_logging:
                        logging.log(TRACE, "NODEID:" +
                                    str(self.__id) + " #14reset")
                    reset_ids.append(index)
                    index += 1
                    reset_flag = True
                    rebroadcast = True

                elif z_ij == float("-inf"):
                    if self.__enable_logging:
                        logging.log(TRACE, "NODEID:" + str(self.__id) + " #16")
                    rebroadcast = True
                    index += 1

                elif z_ij != i and z_ij != k:
                    if self.__enable_logging:
                        logging.log(TRACE, "NODEID:" + str(self.__id) + " #15")
                    rebroadcast = True
                    index += 1

                else:
                    if self.__enable_logging:
                        logging.log(TRACE, "NODEID:" +
                                    str(self.__id) + " #15else")
                    rebroadcast = True
                    index += 1

            elif z_kj == float("-inf"):
                if z_ij == i:
                    if self.__enable_logging:
                        logging.log(TRACE, "NODEID:" + str(self.__id) + " #31")
                    rebroadcast = True
                    index += 1

                elif z_ij == k:
                    if self.__enable_logging:
                        logging.log(TRACE, "NODEID:" + str(self.__id) + " #32")
                    index = self.__update_local_val(
                        tmp_local,
                        index,
                        z_kj,
                        y_kj,
                        t_kj,
                    )
                    rebroadcast = True

                elif z_ij == float("-inf"):
                    if self.__enable_logging:
                        logging.log(TRACE, "NODEID:" + str(self.__id) + " #34")
                    index += 1

                elif z_ij != i and z_ij != k:
                    if t_kj > t_ij:
                        if self.__enable_logging:
                            logging.log(TRACE, "NODEID:" +
                                        str(self.__id) + " #33")
                        index = self.__update_local_val(
                            tmp_local,
                            index,
                            z_kj,
                            y_kj,
                            t_kj,
                        )
                        rebroadcast = True
                    else:
                        if self.__enable_logging:
                            logging.log(TRACE, "NODEID:" +
                                        str(self.__id) + " #33else")
                        index += 1

                else:
                    if self.__enable_logging:
                        logging.log(TRACE, "NODEID:" +
                                    str(self.__id) + " #33elseelse")
                    index += 1
                    rebroadcast = True

            elif z_kj != i and z_kj != k:
                if z_ij == i:
                    if y_kj > y_ij:
                        if self.__enable_logging:
                            logging.log(TRACE, "NODEID:" +
                                        str(self.__id) + "#16")
                        rebroadcast = True
                        index = self.__update_local_val(
                            tmp_local,
                            index,
                            z_kj,
                            y_kj,
                            t_kj,
                        )
                    elif y_kj == y_ij and z_kj < z_ij:
                        if self.__enable_logging:
                            logging.log(TRACE, "NODEID:" +
                                        str(self.__id) + "#17")
                        rebroadcast = True
                        index = self.__update_local_val(
                            tmp_local,
                            index,
                            z_kj,
                            y_kj,
                            t_kj,
                        )
                    else:
                        if self.__enable_logging:
                            logging.log(TRACE, "NODEID:" +
                                        str(self.__id) + "#19")
                        rebroadcast = True
                        index = self.__update_local_val(
                            tmp_local,
                            index,
                            z_ij,
                            tmp_local["bid"][index],
                            bid_time,
                        )

                elif z_ij == k:
                    if y_kj > y_ij:
                        if self.__enable_logging:
                            logging.log(
                                TRACE, "NODEID:" +
                                str(self.__id) + " #20Flavio"
                            )
                        index = self.__update_local_val(
                            tmp_local,
                            index,
                            z_kj,
                            y_kj,
                            t_kj,
                        )
                        rebroadcast = True
                    elif t_kj > t_ij:
                        if self.__enable_logging:
                            logging.log(TRACE, "NODEID:" +
                                        str(self.__id) + "#20")
                        index = self.__update_local_val(
                            tmp_local,
                            index,
                            z_kj,
                            y_kj,
                            t_kj,
                        )
                        rebroadcast = True
                    else:
                        if self.__enable_logging:
                            logging.log(TRACE, "NODEID:" +
                                        str(self.__id) + "#21reset")
                        index += 1
                        rebroadcast = True

                elif z_ij == z_kj:
                    if t_kj > t_ij:
                        if self.__enable_logging:
                            logging.log(TRACE, "NODEID:" +
                                        str(self.__id) + "#22")
                        index = self.__update_local_val(
                            tmp_local,
                            index,
                            z_kj,
                            y_kj,
                            t_kj,
                        )
                        rebroadcast = True
                    else:
                        if self.__enable_logging:
                            logging.log(TRACE, "NODEID:" +
                                        str(self.__id) + " #23 - 24")
                        index += 1

                elif z_ij == float("-inf"):
                    if self.__enable_logging:
                        logging.log(TRACE, "NODEID:" + str(self.__id) + "#30")
                    index = self.__update_local_val(
                        tmp_local,
                        index,
                        z_kj,
                        y_kj,
                        t_kj,
                    )
                    rebroadcast = True

                elif z_ij != i and z_ij != k and z_ij != z_kj:
                    if y_kj >= y_ij and t_kj >= t_ij:
                        if self.__enable_logging:
                            logging.log(TRACE, "NODEID:" +
                                        str(self.__id) + "#25")
                        index = self.__update_local_val(
                            tmp_local,
                            index,
                            z_kj,
                            y_kj,
                            t_kj,
                        )
                        rebroadcast = True
                    elif y_kj < y_ij and t_kj < t_ij:
                        if self.__enable_logging:
                            logging.log(TRACE, "NODEID:" +
                                        str(self.__id) + "#26")
                        rebroadcast = True
                        index += 1
                    elif y_kj < y_ij and t_kj > t_ij:
                        if self.__enable_logging:
                            logging.log(TRACE, "NODEID:" +
                                        str(self.__id) + "#28")
                        index = self.__update_local_val(
                            tmp_local,
                            index,
                            z_kj,
                            y_kj,
                            t_kj,
                        )
                        rebroadcast = True
                    elif y_kj > y_ij and t_kj < t_ij:
                        if self.__enable_logging:
                            logging.log(TRACE, "NODEID:" +
                                        str(self.__id) + "#29")
                        index += 1
                        rebroadcast = True
                    else:
                        if self.__enable_logging:
                            logging.log(TRACE, "NODEID:" +
                                        str(self.__id) + "#29else")
                        index += 1

                else:
                    if self.__enable_logging:
                        logging.log(TRACE, "NODEID:" +
                                    str(self.__id) + " #29else2")
                    index += 1

            else:
                if self.__enable_logging:
                    self.print_node_state("smth wrong?", type="error")

        if reset_flag:
            msg_to_resend = copy.deepcopy(tmp_local)
            for i in reset_ids:
                _ = self.reset(i, tmp_local, bid_time - timedelta(days=1))
                msg_to_resend["auction_id"][i] = self.__item["auction_id"][i]
                msg_to_resend["bid"][i] = self.__item["bid"][i]
                msg_to_resend["timestamp"][i] = self.__item["timestamp"][i]

            with bids_lock:
                bids[self.__item["job_id"]] = copy.deepcopy(tmp_local)
            self.__forward_to_neighbohors(msg_to_resend)
            return False

        cpu = 0
        gpu = 0
        bw = 0
        mem = 0

        first_1 = False
        first_2 = False
        for i in range(len(tmp_local["auction_id"])):
            if (tmp_local["auction_id"][i] == self.__id and prev_bet["auction_id"][i] != self.__id):
                cpu -= self.__item["Bundle_cpus"][i]
                gpu -= self.__item["Bundle_gpus"][i]
                bw -= self.__item["Bundle_bw"][i]
                mem -= self.__item["Bundle_memory"][i]
                if not first_1:
                    first_1 = True
            elif (tmp_local["auction_id"][i] != self.__id and prev_bet["auction_id"][i] == self.__id):
                cpu += self.__item["Bundle_cpus"][i]
                gpu += self.__item["Bundle_gpus"][i]
                bw += self.__item["Bundle_bw"][i]
                mem += self.__item["Bundle_memory"][i]

                if not first_2:
                    first_2 = True

        self.__updated_cpu += cpu
        self.__updated_gpu += gpu
        self.__updated_bw += bw
        self.__updated_memory += mem

        with bids_lock:
            bids[self.__item["job_id"]] = copy.deepcopy(tmp_local)

        return rebroadcast

    
    def __update_bid(self, bidfunc):
        global bids, bids_lock
        if self.__enable_logging:
            self.print_node_state("BEFORE", True)

        if "auction_id" in self.__item:
            consensus = False
            with bids_lock:
                if (bids[self.__item["job_id"]]["auction_id"] == self.__item["auction_id"]
                    and bids[self.__item["job_id"]]["bid"] == self.__item["bid"]
                    and bids[self.__item["job_id"]]["timestamp"] == self.__item["timestamp"]
                    and float("-inf") not in bids[self.__item["job_id"]]["auction_id"]):
                    consensus = True
            
            if consensus:
                if self.__enable_logging:
                    self.print_node_state("Consensus -", True)
                    # pass
            else:
                rebroadcast = self.__deconfliction()
                success = bidfunc()

                return success or rebroadcast
        else:
            bidfunc()
            return True

    def __check_if_hosting_job(self):
        global bids, bids_lock
        with bids_lock:
            if (
                self.__item["job_id"] in bids
                and self.__id in bids[self.__item["job_id"]]["auction_id"]
            ):
                return True
            return False

    def __release_resources(self):
        global bids, bids_lock
        cpu = 0
        gpu = 0

        with bids_lock:
            for i, id in enumerate(bids[self.__item["job_id"]]["auction_id"]):
                if id == self.__id:
                    cpu += self.__item["Bundle_cpus"][i]
                    gpu += self.__item["Bundle_gpus"][i]

        self.__updated_cpu += cpu
        self.__updated_gpu += gpu

    def start_daemon(self, stop_event=None):
        self.__daemon = threading.Thread(
            target=self.__work, args=(stop_event,))
        self.__daemon.start()

    def __work(self, end_processing):
        global bids, bids_lock 

        failure = False
        failure_duration = 0       

        while True:
            try:
                self.__item = None
                items = self.__extract_all_job_msg()
                first_msg = False
                need_rebroadcast = False

                for it in items:
                    self.__item = it

                    if not failure:
                        r = random.randrange(0, 100)
                        if r == 56:
                            failure = True
                            failure_duration = random.randrange(1, 10)
                            self.__httpd.shutdown()

                    if failure:
                        continue

                    if self.__item["type"] == "unallocate":
                        if self.__check_if_hosting_job():
                            self.__release_resources()

                        with bids_lock:
                            if self.__item["job_id"] in bids:
                                del bids[self.__item["job_id"]]
                                del self.__counter[self.__item["job_id"]]
                    else:
                        first_msg = False

                        if self.__item["job_id"] not in self.__counter:
                            self.__init_null()
                            first_msg = True
                            self.__counter[self.__item["job_id"]] = 0
                            if self.__item["edge_id"] == None:
                                self.__tasks_from_clients.append(self.__item["job_id"])
                        self.__counter[self.__item["job_id"]] += 1

                        # differentiate bidding based on the type of the message
                        if self.__item["type"] == "topology":
                            success = self.__update_bid(self.__bid_topology)
                        elif self.__item["type"] == "allocate":
                            success = self.__update_bid(self.__bid)

                        need_rebroadcast = need_rebroadcast or success

                if need_rebroadcast:
                    self.__forward_to_neighbohors()
                elif first_msg:
                    self.__forward_to_neighbohors(first_msg=True)

            except Empty:
                if failure:
                    failure_duration -= 1
                    if failure_duration == 0:
                        failure = False
                        self.__run_http_server()
                if end_processing is not None and end_processing.is_set():
                    return

    def __extract_all_job_msg(self):
        global q
        first = True
        job_id = None
        items = []
        _items = []
        while True:
            try:
                it = q.get(timeout=self.__timeout)
                if first:
                    first = False
                    job_id = it["job_id"]
                if job_id == it["job_id"]:
                    items.append(it)
                else:
                    _items.append(it)

                if not self.__reduce_packets:
                    raise Empty
            except Empty:
                if len(items) == 0:
                    raise Empty

                for i in _items:
                    q[self.__id].put(i)
                break

        return items
