import os
import shutil
import random
import MySQLdb
import hashlib
import datetime
import ConfigParser
import binascii
import socket
from time import sleep
from subprocess import Popen, PIPE


def ip_to_hex(ip):
    return binascii.hexlify(socket.inet_aton(ip)).upper()


def write_in_log(wil_message, wil_ip=''):

    try:
        wil_log_file = open(path_to_log_file, 'a', buffering=-1)
    except IOError as e:
        print "Can not open log file. I/O Error({0}): {1}".format(e.errno, e.strerror)
        exit(1)
    else:
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if wil_ip != '':
            wil_result_message = date_time + " " + wil_ip + " " + wil_message
        else:
            wil_result_message = date_time + " " + wil_message

        print wil_result_message

        del date_time

        wil_log_file.write(wil_result_message + '\n')
        wil_log_file.close()


def do_backup_config(dbc_ip, dbc_community, dbc_type, dbc_tftp, dbc_file_name):

    if dbc_type in [15, 17, 24, 25, 41]:

        # Type of support switches:
        # 15 - D-link DES-3526
        # 17 - D-link DES-3200-28 hw A1/B1
        # 24 - D-link DGS-3200-16
        # 25 - D-link DES-3200-18 hw A1/B1
        # 41 - D-link DES-3200-26 hw A1/B1

        snmp_command = "snmpset -v2c -c " + dbc_community + " " + dbc_ip + " \
                    1.3.6.1.4.1.171.12.1.2.1.1.3.3 a " + dbc_tftp + " \
                    1.3.6.1.4.1.171.12.1.2.1.1.4.3 i 2 \
                    1.3.6.1.4.1.171.12.1.2.1.1.5.3 s dlink/" + dbc_file_name + " \
                    1.3.6.1.4.1.171.12.1.2.1.1.7.3 i 2 \
                    1.3.6.1.4.1.171.12.1.2.1.1.8.3 i 3"

    elif dbc_type in [27, 28, 29, 30, 32, 33, 39, 40]:

        # Type of support switches:
        # 27 - D-link DES-3200-26 hw C1
        # 28 - D-link DGS-3620-28SC
        # 29 - D-link DGS-3120-24SC
        # 30 - D-link DES-3200-52
        # 32 - D-link DGS-3620-28TC
        # 33 - D-link DES-3200-28F
        # 39 - D-link DES-3200-28 hw C1
        # 40 - D-link DES-3200-18 hw C1

        snmp_command = "snmpset -v2c -c " + dbc_community + " " + dbc_ip + " \
                    1.3.6.1.4.1.171.12.1.2.18.1.1.3.3 a " + dbc_tftp + " \
                    1.3.6.1.4.1.171.12.1.2.18.1.1.5.3 s dlink/" + dbc_file_name + " \
                    1.3.6.1.4.1.171.12.1.2.18.1.1.8.3 i 2 \
                    1.3.6.1.4.1.171.12.1.2.18.1.1.12.3 i 3"

    elif dbc_type in [35]:

        # Type of support switches:
        # 35 - D-link DGS-1100-10/ME

        snmp_command = "snmpset -v2c -c " + dbc_community + " " + dbc_ip + " \
                    1.3.6.1.4.1.171.10.134.2.1.3.2.1.0 x " + ip_to_hex(dbc_tftp) + " \
                    1.3.6.1.4.1.171.10.134.2.1.3.2.2.0 i 1 \
                    1.3.6.1.4.1.171.10.134.2.1.3.2.4.0 s dlink/" + dbc_file_name + " \
                    1.3.6.1.4.1.171.10.134.2.1.3.2.5.0 i 2"

#    elif dbc_type in [37]:

        # Type of support switches:
        # 35 - D-link DGS-1100-10/ME

#        Popen("snmpset -v2c -c " + dbc_community + " " + dbc_ip + " \
#                   1.3.6.1.4.1.171.10.139.3.1.1.1.2.4.2.0 x C0A810B4 \
#                   1.3.6.1.4.1.171.10.139.3.1.1.1.2.4.3.0 s dlink/" + dbc_file_name + " \
#                   1.3.6.1.4.1.171.10.139.3.1.1.1.2.4.4.0 i 1 \
#                   1.3.6.1.4.1.171.10.139.3.1.1.1.2.4.6.0 i 2",
#              shell=True, stdin=PIPE, stdout=PIPE).stdout.read().split()

    else:

        snmp_command = ''

        write_in_log("I do not know how to do backup from this switch", dbc_ip)
        print "I do not know how to do backup from this switch. " + dbc_ip

    if snmp_command != '':
        Popen(snmp_command, shell=True, stdin=PIPE, stdout=PIPE).stdout.read().split()
        return True
    else:
        return False


def get_md5_sum(gms_file_name):
    m = hashlib.md5()
    fd = open(gms_file_name, 'rb')
    b = fd.read()
    m.update(b)
    fd.close()
    return m.hexdigest()


def check_config(cc_device_id, cc_hash):
    cursor3 = db.cursor()
    cursor3.execute("SELECT hash FROM `" + table_name + "` WHERE `devid` = '" + cc_device_id + "'\
                    ORDER BY date DESC LIMIT 1")
    for cc_row in cursor3.fetchall():
        if cc_row[0] == cc_hash:
            return True
        else:
            return False


def move_file_to_archive(mfta_file_name):
    shutil.move(os.path.join(path_to_tftp_folder, mfta_file_name), os.path.join(path_to_archive, mfta_file_name))


def remove_file(rf_file_name):
    os.remove(path_to_tftp_folder + rf_file_name)


def get_random_word():
    i = 0
    grw_word = ''
    while i < 3:
        i += 1
        grw_word = grw_word + random.choice("wertyupasdfghkzxcvbnm0123456789ijq")
    return grw_word


config = ConfigParser.ConfigParser()
config.read('config.cfg')

ip_tftp_server = config.get('tftp', 'ip')
path_to_tftp_folder = config.get('tftp', 'path_to_tftp_folder')
path_to_archive = config.get('archive', 'path_to_archive')
path_to_log_file = config.get('log', 'path_to_log_file')
host_name = config.get('database', 'host')
user_name = config.get('database', 'user')
password = config.get('database', 'passwd')
db_name = config.get('database', 'db')
table_name = config.get('database', 'table')

db = MySQLdb.connect(host=host_name,
                     user=user_name,
                     passwd=password,
                     db=db_name)

cursor = db.cursor()

cursor.execute("SELECT `ip`, `access_snmp_write`, `devices`.`type`, `id` \
                FROM `devices` \
                LEFT JOIN `devices_config` \
                    ON `devices`.`type` = `devices_config`.`type` \
                WHERE `ping` = '1' \
                    AND `devices_config`.`do_backup` = '1' \
                LIMIT 15")

for row in cursor.fetchall():

    ip_address = str(row[0])
    snmp_community = str(row[1])
    device_type = row[2]
    device_id = str(row[3])

    file_name = ip_address + "_" + str(datetime.date.today()) + "_" + get_random_word() + ".cfg"
    if do_backup_config(ip_address, snmp_community, device_type, ip_tftp_server, file_name):
        sleep(5)
        if os.path.isfile(path_to_tftp_folder + file_name):
            md5_hash = str(get_md5_sum(path_to_tftp_folder + file_name))

            if check_config(device_id, md5_hash):
                write_in_log("Config file was not updated in last time", ip_address)
                remove_file(file_name)
            else:
                move_file_to_archive(file_name)
                cursor.execute("insert into `" + table_name + "` (devid, fname, hash)\
                                VALUES(" + device_id + ", '" + file_name + "', '" + md5_hash + "')")
                db.commit()
                write_in_log("Config was updated...", ip_address)
        else:
            write_in_log("File not found", device_id)

db.commit()
db.close()
