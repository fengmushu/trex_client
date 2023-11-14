from trex_stl_lib.api import *
from trex.stl.trex_stl_hltapi import *


class STLS1(object):

    def create_stream(self):
        return STLHltStream(
            frame_size=1400,
            ignore_macs=True,
            l3_protocol='ipv4',
            ip_src_addr='192.168.10.3',
            ip_src_mode='fixed',
            ip_dst_addr='192.168.10.4',
            ip_dst_mode='fixed',
            l4_protocol='udp',
            udp_src_port=1025,
            udp_src_port_mode='fixed',
            udp_dst_port=1025,
            udp_dst_port_mode='fixed',
            direction=1,
            flow_stats_id=4,
        )
        # return STLStream(
        #     name="P4-UDP",
        #     packet=STLPktBuilder(
        #         pkt=Ether()/IP(src="192.168.10.4", dst="192.168.10.3") /
        #         UDP(dport=1025, sport=1025)/(1400*'x')
        #     ),
        #     mode=STLTXCont(),
        #     stream_id=4
        # )

    def get_streams(self, direction=0, **kwargs):
        # create 1 stream
        return [self.create_stream()]


# dynamic load - used for trex console or simulator
def register():
    return STLS1()
