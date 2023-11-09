import stl_path
from trex.stl.api import *

import time


def simple():

    # create client
    # verbose_level = 'high'
    c = STLClient(verbose_level='error', server='10.10.16.241')
    passed = True

    try:
        # connect to server
        c.connect()

        acquire_ports = [0, 1, 2, 3]

        # prepare our ports
        c.reset(ports=acquire_ports)

        print((" is connected {0}".format(c.is_connected())))

        print((" number of ports {0}".format(c.get_port_count())))
        print((" acquired_ports {0}".format(c.get_acquired_ports())))
        # port stats
        print(c.get_stats(acquire_ports))
        # port info
        print(c.get_port_info(acquire_ports))

        # all 4 ports
        print(c.get_all_ports())

        # c.ping()
        c.service_line('-a')
        c.arp()

        profile_file_1 = os.path.join(
            stl_path.STL_PROFILES_PATH, 'udp_1pkt_1.py')
        profile_file_2 = os.path.join(
            stl_path.STL_PROFILES_PATH, 'udp_1pkt_2.py')
        profile_file_3 = os.path.join(
            stl_path.STL_PROFILES_PATH, 'udp_1pkt_3.py')
        profile_file_4 = os.path.join(
            stl_path.STL_PROFILES_PATH, 'udp_1pkt_4.py')

        print("start")
        c.start_line(" -f {} -m 99% --port 0 --force ".format(profile_file_1))
        c.start_line(" -f {} -m 99% --port 1 --force ".format(profile_file_2))
        c.start_line(" -f {} -m 99% --port 2 --force ".format(profile_file_3))
        c.start_line(" -f {} -m 99% --port 3 --force ".format(profile_file_4))
        # print(c.profiles_line('-a'))
        print(c.streams_line('-a'))
        time.sleep(5)

        # c.pause_line("--port 0 1")
        # time.sleep(2)
        # c.resume_line("--port 0 1")
        # time.sleep(2)
        print("step up... 50%")
        c.update_line("--port 0 -m 1% -t ")
        c.update_line("--port 1 -m 1% -t ")
        c.update_line("--port 2 -m 1% -t ")
        c.update_line("--port 3 -m 1% -t ")
        print(c.streams_line('-a'))
        time.sleep(30)

        c.stop_line("--port 0 1 2 3")
        c.release_line("--port 0 1 2 3")

    except STLError as e:
        passed = False
        print(e)

    finally:
        c.disconnect()

    if passed:
        print("\nTest has passed :-)\n")
    else:
        print("\nTest has failed :-(\n")


# run the tests
simple()
