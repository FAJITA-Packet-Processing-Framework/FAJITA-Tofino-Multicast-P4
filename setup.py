import json
import time
import os

p4 = bfrt.fajita_mcast

ENABLE_RECIRCULATION = 1

MCAST_PORTS = [188, 180, 172, 164]

previous_received_pkts_count = 0
previous_received_bytes_count = 0
previous_sent_pkts_count = 0
previous_sent_bytes_count = 0

start_ts = time.time()


def run_pd_rpc(cmd_or_code, no_print=False):
    """
    This function invokes run_pd_rpc.py tool. It has a single string argument
    cmd_or_code that works as follows:
       If it is a string:
            * if the string starts with os.sep, then it is a filename
            * otherwise it is a piece of code (passed via "--eval"
       Else it is a list/tuple and it is passed "as-is"

    Note: do not attempt to run the tool in the interactive mode!
    """
    import subprocess

    path = os.path.join("/home", "tofino", "tools", "run_pd_rpc.py")

    command = [path]
    if isinstance(cmd_or_code, str):
        if cmd_or_code.startswith(os.sep):
            command.extend(["--no-wait", cmd_or_code])
        else:
            command.extend(["--no-wait", "--eval", cmd_or_code])
    else:
        command.extend(cmd_or_code)

    result = subprocess.check_output(command).decode("utf-8")[:-1]
    if not no_print:
        print(result)

    return result


def port_stats():
    import struct

    global bfrt, previous_received_pkts_count, previous_received_bytes_count, previous_sent_pkts_count, \
        previous_sent_bytes_count, time, start_ts, MCAST_PORTS

    mcast_ports_stats = []
    for port in MCAST_PORTS:
        mcast_ports_stats.append(bfrt.port.port_stat.get(DEV_PORT=port, print_ents=False))

    total_pkts_received = 0
    total_bytes_received = 0
    total_pkts_sent = 0
    total_bytes_sent = 0
    for port_stat in mcast_ports_stats:
        total_pkts_received += port_stat.data[b'$FramesReceivedOK']
        total_bytes_received += port_stat.data[b'$OctetsReceived']
        total_pkts_sent += port_stat.data[b'$FramesTransmittedOK']
        total_bytes_sent += port_stat.data[b'$OctetsTransmittedTotal']

    ts = time.time() - start_ts

    delta_recv_bytes = total_bytes_received - previous_received_bytes_count
    delta_sent_bytes = total_bytes_sent - previous_sent_bytes_count
    delta_recv_pkts = total_pkts_received - previous_received_pkts_count
    delta_sent_pkts = total_pkts_sent - previous_sent_pkts_count

    print("TOF-%f-RESULT-TOFRX %f" % (ts, delta_recv_bytes * 8))
    print("TOF-%f-RESULT-TOFTX %f" % (ts, delta_sent_bytes * 8))
    print("TOF-%f-RESULT-TOFRXPPS %f" % (ts, delta_recv_pkts))
    print("TOF-%f-RESULT-TOFTXPPS %f" % (ts, delta_sent_pkts))

    previous_received_pkts_count = total_pkts_received
    previous_received_bytes_count = total_bytes_received
    previous_sent_pkts_count = total_pkts_sent
    previous_sent_bytes_count = total_bytes_sent


def port_stats_timer():
    import threading

    global port_stats_timer, port_stats
    port_stats()
    threading.Timer(1, port_stats_timer).start()


script_path = os.path.join(os.environ['HOME'], "labs", "fajita_mcast")

run_pd_rpc(os.path.join(script_path, "run_pd_rpc", "setup.py"))

p4.pipe.Ingress.enable_recirculation.add(f1=ENABLE_RECIRCULATION, REGISTER_INDEX=0)

port_stats_timer()
