import os
import argparse
import sys
import shutil
import telnetlib
import random
from subprocess import Popen, PIPE


def create_parser():
    cp_parser = argparse.ArgumentParser()
    cp_parser.add_argument('--device_id', type=int)
    cp_parser.add_argument('--device_type', type=int)
    cp_parser.add_argument('--config_id', type=int)
    cp_parser.add_argument('--ip_address', default='10.90.90.90')
    cp_parser.add_argument('--config_file_name')

    return cp_parser


def check_ping(cp_ip_address):
    output = Popen("ping -c 1 -W 1 " + cp_ip_address, shell=True, stdin=PIPE, stdout=PIPE).communicate()[0]

    if '100% packet loss' in output:
        return False
    else:
        return True


def copy_config_file_to_tftp_folder(local_config_file_name):
    shutil.copy(os.path.join(r'/usr/local/src/backup/configs/', local_config_file_name),
                os.path.join(r'/srv/tftp/', local_config_file_name))


def get_random_word():
    i = 0
    word = ''
    while i < 3:
        i += 1
        word = word + random.choice("0123456789")
    return word


def restore_config():
    rnd_config_name = "config" + get_random_word() + ".cfg"

    tn = telnetlib.Telnet(ip_address)
    tn.read_until("UserName:")
    tn.write("\n")
    tn.read_until("PassWord:")
    tn.write("\n")

    tn.read_until("admin#")
    tn.write("download cfg_fromTFTP 10.90.90.91 src_file " + config_file_name + " dest_file " + rnd_config_name + "\n")
    tn.read_until("admin#")
    tn.write("config configuration " + rnd_config_name + " boot_up\n")
    tn.read_until("admin#")
    tn.write("reboot force_agree\n")


parser = create_parser()
namespace = parser.parse_args(sys.argv[1:])

device_id = namespace.device_id
config_id = namespace.config_id
ip_address = namespace.ip_address
device_type = namespace.device_type
config_file_name = namespace.config_file_name

print str(device_id) + " " + str(config_id) + " " + str(ip_address) + " " + str(config_file_name)

if check_ping(ip_address):
    copy_config_file_to_tftp_folder(config_file_name)
    restore_config()
    print "Online"
else:
    print "Offline"
