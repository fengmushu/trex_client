import stl_path
from trex.stl.api import *
from trex.stl.trex_stl_hltapi import *
from trex.examples.stl.stl_broker import *

import time
import signal
import os
import json
import zlib


class StlBocker(object):

    def __init__(self) -> None:
        self.running = True
        self.hlt = CTRexHltApi(verbose='info')
        self.nv = StlBrokerConfig()
        self.nv.sync()
        self.vlans = self.nv.get(
            "PortVlans", {
                0: [11, 12, 13, 14, 15, 16, 17, 18, 19],
                1: [21, 22, 23, 24, 25, 26, 27, 28, 29],
                2: [31, 32, 33, 34, 35, 36, 37, 38, 39],
                3: [41, 42, 43, 44, 45, 46, 47, 48]})
        self.username = ("cli-EB"),
        self.ports = self.nv.get("PortsAcquire", [0, 1])
        self.server_addr = self.nv.get('ServerAddr', '10.10.16.241')
        pass

    def stop(self):
        self.running = False

    def vlan_getid(self, port=-1, idx=-1) -> int:
        vlanid = self.vlans[port][idx]
        return vlanid

    def build_stream(self, vlan_offset=0, mode='create'):
        for p in self.ports:
            if p % 2 == 0:
                src = 1
                dst = 2
            else:
                src = 2
                dst = 1
            vlan_id = 10*src+vlan_offset+1
            self.cli.clear_vlan(ports=p)
            self.cli.set_vlan(ports=p, vlan=vlan_id)
            res = self.hlt.traffic_config(mode=mode,
                                          vlan_id=vlan_id,
                                          vlan_id_mode="fixed",
                                          bidirectional=False,
                                          port_handle=p,
                                          frame_size=1400,
                                          ignore_macs=True,
                                          l3_protocol='ipv4',
                                          ip_src_addr='192.168.10.{}'.format(
                                              src),
                                          ip_src_mode='fixed',
                                          ip_dst_addr='192.168.10.{}'.format(
                                              dst),
                                          ip_dst_mode='fixed',
                                          l4_protocol='udp',
                                          udp_src_port=1025,
                                          udp_src_port_mode='fixed',
                                          udp_dst_port=1025,
                                          udp_dst_port_mode='fixed',
                                          flow_stats_id=src,
                                          stream_id=src,
                                          )
            check_res(res)

    def vlan_update(self, vlan_idx=0):
        self.cli.stop(ports=self.ports, rx_delay_ms=100)
        self.build_stream(vlan_offset=vlan_idx, mode='modify')
        try:
            self.cli.arp(ports=self.ports, verbose=True)
            self.cli.clear_stats(ports=self.ports,
                                 #  clear_global=True,
                                 clear_flow_stats=True)
            self.cli.start(ports=self.ports, force=True, mult="100%")
        except Exception as e:
            print(e)
            pass

    def test_run(self):
        print("connect to {} ports: {}".format(self.server_addr, self.ports))
        res = self.hlt.connect(
            device=self.server_addr,
            port_list=self.ports,
            reset=True,
            break_locks=True)
        check_res(res)
        self.cli = self.hlt.trex_client
        self.ports = list(res['port_handle'].values())

        # service and arp
        self.cli.set_service_mode(ports=self.ports, enabled=True)

        print('Creating traffic')
        self.build_stream()

        try:
            vlan_idx = 0
            while self.running == True:
                if self.nv.dirty('RateP_N'):
                    rate = self.nv.get("RateP_0", 0.1)
                    self.hlt.traffic_config(mode="modify",
                                            rate_percent="{}".format(rate))
                if True:  # self.nv.dirty("VlanIdx"):
                    idx = self.nv.get("VlanIdx", -1)
                    if idx < 0:
                        idx = vlan_idx
                    try:
                        self.vlan_update(idx)
                        wait_with_progress(10)
                        res = self.hlt.traffic_stats(
                            mode='aggregate', port_handle=self.ports)
                        check_res(res)
                        print_brief_stats(res)
                    except Exception as e:
                        print(e)
                    vlan_idx += 1
                    if vlan_idx > 3:
                        vlan_idx = 0

        except Exception as e:
            pass
        finally:
            self.cli.stop(ports=self.ports)
            self.cli.release(ports=self.ports)
        self.hlt.cleanup_session(port_handle='all')


gc = StlBocker()


def sig_handle(sig, frame):
    print("On signal: ", sig)
    global gc
    if sig == signal.SIGTERM or sig == signal.SIGINT:
        gc.stop()

    if sig == signal.SIGTERM:
        gc.nv.write()

    # other SIGUSR1..., update config
    gc.nv.sync()
    return


if __name__ == '__main__':
    signal.signal(signal.SIGINT, sig_handle)
    signal.signal(signal.SIGHUP, sig_handle)
    signal.signal(signal.SIGTERM, sig_handle)
    signal.signal(signal.SIGUSR1, sig_handle)
    gc.test_run()
