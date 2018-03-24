#!/usr/bin/env python

import os
import shutil
import random
import MySQLdb
import hashlib
import datetime
import telnetlib
import threading
import ConfigParser
import binascii
import socket
import time
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


def do_backup_config(dbc_ip, dbc_community, dbc_type, dbc_tftp, dbc_file_name, dbc_access_username,
                     dbc_access_password):

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

    elif dbc_type in [23]:

        # Type of support switches:
        # 23 - D-link DGS-3627G

        snmp_command = "Telnet"

        tn = telnetlib.Telnet(dbc_ip)

        tn.read_until('UserName:', 5)

        tn.write(dbc_access_username)
        time.sleep(1)

        tn.write("\r")
        time.sleep(1)

        tn.write(dbc_access_password)
        time.sleep(1)

        tn.write("\r")
        tn.read_until("#")
        tn.write("upload cfg_toTFTP " + dbc_tftp + " dest_file dlink/" + dbc_file_name + "\n")
        time.sleep(15)
        tn.read_until("DGS-3627G:admin#")
        tn.write("logout\n")

    elif dbc_type in [19]:

        # Type of support switches:
        # 19 - D-link DGS-3100-24TG

        snmp_command = "Telnet"

        tn = telnetlib.Telnet(dbc_ip)

        tn.read_until('UserName:', 5)

        tn.write(dbc_access_username)
        time.sleep(1)

        tn.write("\r")
        time.sleep(1)

        tn.write(dbc_access_password)
        time.sleep(1)

        tn.write("\r")
        time.sleep(1)

        tn.write("\r")
        tn.read_until("#")
        tn.write("upload configuration " + dbc_tftp + " dlink/" + dbc_file_name + "\n")
        time.sleep(5)
        tn.read_until("#")
        tn.write("logout\n")

    elif dbc_type in [38]:

        # Type of support switches:
        # 38 - ELTEX LTE-8x

        snmp_command = "Telnet"

        tn = telnetlib.Telnet(dbc_ip)

        tn.read_until('login: ', 3)

        tn.write(dbc_access_username)
        tn.write("\r")

        tn.read_until('Password: ', 3)

        tn.write(dbc_access_password)
        tn.write("\r")
        sleep(3)

        tn.read_until('LTE-2X# ', 5)
        tn.write("upload config backup /dlink/" + dbc_file_name + " " + dbc_tftp + "\n")
        tn.write("\r")
        tn.read_until("LTE-2X# ", 5)
        tn.write('exit' + '\n')

    elif dbc_type in [43]:

        # Type of support switches:
        # 43 - ELTEX LTP-8x

        snmp_command = "Telnet"

        tn = telnetlib.Telnet(dbc_ip)

        tn.read_until('login: ', 3)

        tn.write(dbc_access_username)
        tn.write("\r")

        tn.read_until('Password: ', 3)

        tn.write(dbc_access_password)
        tn.write("\r")
        sleep(3)

        tn.read_until('LTP-8X# ', 5)
        tn.write("copy fs://config tftp://" + dbc_tftp + "/dlink/" + dbc_file_name + "\n")
        tn.write("\r")
        tn.read_until("LTP-8X# ", 5)
        tn.write('exit' + '\n')


#    elif dbc_type in [37]:

        # Type of support switches:
        # 37 - Dlink DXS-1210-12SC

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

    if snmp_command == '':
        return False
    elif snmp_command == 'Telnet':
        return True
    else:
        Popen(snmp_command, shell=True, stdin=PIPE, stdout=PIPE).stdout.read().split()
        return True


def get_md5_sum(gms_file_name):
    m = hashlib.md5()
    fd = open(gms_file_name, 'rb')
    b = fd.read()
    m.update(b)
    fd.close()
    return m.hexdigest()


def check_config(cc_device_id, cc_hash):
    cc_db = MySQLdb.connect(host=host_name, user=user_name, passwd=password, db=db_name)
    cursor3 = cc_db.cursor()
    cursor3.execute("SELECT hash FROM `" + table_name + "` WHERE `devid` = '" + cc_device_id + "'\
                    ORDER BY date DESC LIMIT 1")
    cc_db.commit()
    cc_db.close()
    for cc_row in cursor3.fetchall():
        if cc_row[0] == cc_hash:
            return True
        else:
            return False


def move_file_to_archive(mfta_file_name):
    shutil.move(os.path.join(path_to_tftp_folder, mfta_file_name), os.path.join(path_to_archive, mfta_file_name))


def remove_file(rf_file_name, rf_path_to_folder):
    os.remove(rf_path_to_folder + rf_file_name)


def get_random_word():
    i = 0
    grw_word = ''
    while i < 3:
        i += 1
        grw_word = grw_word + random.choice("wertyupasdfghkzxcvbnm0123456789ijq")
    return grw_word


def delete_config(config_name):
    dc_db = MySQLdb.connect(host=host_name, user=user_name, passwd=password, db=db_name)
    cursor = dc_db.cursor()
    remove_file(config_name, path_to_archive)
    cursor.execute("DELETE FROM `" + table_name + "` WHERE `" + table_name + "`.`fname` = '" + config_name + "'")
    write_in_log("Config " + config_name + " was deleted.")
    dc_db.commit()
    dc_db.close()


def check_duplicate_config(device_id, hash):
    cdc_db = MySQLdb.connect(host=host_name, user=user_name, passwd=password, db=db_name)
    cursor3 = cdc_db.cursor()
    cursor3.execute("SELECT fname FROM `" + table_name + "` WHERE `devid` = '" + device_id + "' AND hash = '" + hash + "'\
                        AND date < '" + str(datetime.date.today()) + "'")

    for row in cursor3.fetchall():
        delete_config(row[0])

    cdc_db.commit()
    cdc_db.close()


def delete_old_config(device_id):
    doc_db = MySQLdb.connect(host=host_name, user=user_name, passwd=password, db=db_name)
    cursor4 = doc_db.cursor()
    cursor4.execute("SELECT fname, date"
                    " FROM `" + table_name + "`"
                    " WHERE `devid` = '" + device_id + "' ORDER BY date DESC")

    counter = 0

    for row in cursor4.fetchall():
        counter = counter + 1
        if counter > 5 and str(row[1]) < str(datetime.date.today()-datetime.timedelta(days=60)):
            delete_config(row[0])
            write_in_log("Config " + row[0] + " was deleted. He is too old.")

    doc_db.commit()
    doc_db.close()


def find_deleted_switch():
    cursor5 = db.cursor()
    cursor6 = db.cursor()
    cursor5.execute("SELECT devid"
                    " FROM `" + table_name + "`"
                    " WHERE date < '" + str(datetime.date.today()-datetime.timedelta(days=60)) + "'")

    for row in cursor5.fetchall():
        cursor6.execute("SELECT 1 FROM `devices` WHERE id = " + str(row[0]))
        if cursor6.rowcount == 0:
            cursor6.execute("SELECT fname FROM `" + table_name + "` WHERE `devid` = " + str(row[0]))

            for row2 in cursor6.fetchall():
                delete_config(row2[0])
                write_in_log("Config " + str(row[0]) + " was deleted. Switch was deleted in past.")


def main_function(ip_address, snmp_community, device_type, device_id, access_username, access_password):

    sleep(random.randint(0, 5))

    mf_db = MySQLdb.connect(host=host_name, user=user_name, passwd=password, db=db_name)
    cursor9 = mf_db.cursor()

    file_name = ip_address + "_" + str(datetime.date.today()) + "_" + get_random_word() + ".cfg"

    if device_type == 38:
        file_name = file_name + ".zip"

    if do_backup_config(ip_address, snmp_community, device_type, ip_tftp_server, file_name, access_username,
                        access_password):
        sleep(10)
        if os.path.isfile(path_to_tftp_folder + file_name):
            md5_hash = str(get_md5_sum(path_to_tftp_folder + file_name))

            if check_config(device_id, md5_hash):
                write_in_log("Config file was not updated in last time", ip_address)
                remove_file(file_name, path_to_tftp_folder)
            else:
                move_file_to_archive(file_name)

                check_duplicate_config(device_id, md5_hash)

                cursor9.execute("insert into `" + table_name + "` (devid, fname, hash)\
                                    VALUES(" + device_id + ", '" + file_name + "', '" + md5_hash + "')")
                mf_db.commit()
                mf_db.close()
                write_in_log("Config was updated...", ip_address)
        else:
            write_in_log("File not found", device_id)


        delete_old_config(device_id)


config = ConfigParser.ConfigParser()
config.read(r'/home/dima/PycharmProjects/d-link config backup/config.cfg')

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

cursor.execute("SELECT `ip`, `access_snmp_write`, `devices`.`type`, `id`, `access_username`, `access_password` \
                FROM `devices` \
                LEFT JOIN `devices_config` \
                    ON `devices`.`type` = `devices_config`.`type` \
                WHERE `ping` = '1' \
                    AND `devices_config`.`do_backup` = '1' AND duplicate = '0' ORDER BY `id` \
                LIMIT 1000")

t1 = t2 = t3 = t4 = t5 = t6 = t7 = t8 = t9 = t10 = threading.Thread()

row = cursor.fetchone()

while row is not None:

    t1 = threading.Thread(target=main_function, args=(row[0], row[1], row[2], str(row[3]), row[4], row[5]))
    # print str(row[3]) + " thread 1"

    t1.start()

    row = cursor.fetchone()

    if row is not None:
        t2 = threading.Thread(target=main_function, args=(row[0], row[1], row[2], str(row[3]), row[4], row[5]))
        # print str(row[3]) + " thread 2"
        t2.start()

    row = cursor.fetchone()

    if row is not None:
        t3 = threading.Thread(target=main_function, args=(row[0], row[1], row[2], str(row[3]), row[4], row[5]))
        # print str(row[3]) + " thread 3"
        t3.start()

    row = cursor.fetchone()

    if row is not None:
        t4 = threading.Thread(target=main_function, args=(row[0], row[1], row[2], str(row[3]), row[4], row[5]))
        # print str(row[3]) + " thread 4"
        t4.start()

    row = cursor.fetchone()

    if row is not None:
        t5 = threading.Thread(target=main_function, args=(row[0], row[1], row[2], str(row[3]), row[4], row[5]))
        # print str(row[3]) + " thread 5"
        t5.start()

    row = cursor.fetchone()

    if row is not None:
        t6 = threading.Thread(target=main_function, args=(row[0], row[1], row[2], str(row[3]), row[4], row[5]))
        # print str(row[3]) + " thread 6"
        t6.start()

    row = cursor.fetchone()

    if row is not None:
        t7 = threading.Thread(target=main_function, args=(row[0], row[1], row[2], str(row[3]), row[4], row[5]))
        # print str(row[3]) + " thread 7"
        t7.start()

    row = cursor.fetchone()

    if row is not None:
        t8 = threading.Thread(target=main_function, args=(row[0], row[1], row[2], str(row[3]), row[4], row[5]))
        # print str(row[3]) + " thread 8"
        t8.start()

    row = cursor.fetchone()

    if row is not None:
        t9 = threading.Thread(target=main_function, args=(row[0], row[1], row[2], str(row[3]), row[4], row[5]))
        # print str(row[3]) + " thread 9"
        t9.start()

    row = cursor.fetchone()

    if row is not None:
        t10 = threading.Thread(target=main_function, args=(row[0], row[1], row[2], str(row[3]), row[4], row[5]))
        # print str(row[3]) + " thread 10"
        t10.start()

    t1.join()

    if t2.is_alive():
        t2.join()

    if t3.is_alive():
        t3.join()

    if t4.is_alive():
        t4.join()

    if t5.is_alive():
        t5.join()

    if t6.is_alive():
        t6.join()

    if t7.is_alive():
        t7.join()

    if t8.is_alive():
        t8.join()

    if t9.is_alive():
        t9.join()

    if t10.is_alive():
        t10.join()

    row = cursor.fetchone()


find_deleted_switch()

db.commit()
db.close()

