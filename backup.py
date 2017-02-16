import os
import shutil
import random
import MySQLdb
import hashlib
import datetime
import ConfigParser
from subprocess import Popen, PIPE
from time import sleep


def do_backup_config(dbc_ip, dbc_community, dbc_type, dbc_tftp, dbc_file_name):
    if dbc_type in [17, 25, 41]:
        Popen("snmpset -v2c -c " + dbc_community + " " + dbc_ip + " 1.3.6.1.4.1.171.12.1.2.1.1.3.3 a " + dbc_tftp + " \
            1.3.6.1.4.1.171.12.1.2.1.1.4.3 i 2 \
            1.3.6.1.4.1.171.12.1.2.1.1.5.3 s dlink/" + dbc_file_name + " \
            1.3.6.1.4.1.171.12.1.2.1.1.7.3 i 2 \
            1.3.6.1.4.1.171.12.1.2.1.1.8.3 i 3",
              shell=True, stdin=PIPE, stdout=PIPE).stdout.read().split()
    else:
        Popen("snmpset -v2c -c " + dbc_community + " " + dbc_ip + " 1.3.6.1.4.1.171.12.1.2.18.1.1.3.3 a " + dbc_tftp + " \
            1.3.6.1.4.1.171.12.1.2.18.1.1.5.3 s dlink/" + dbc_file_name + " \
            1.3.6.1.4.1.171.12.1.2.18.1.1.8.3 i 2 \
            1.3.6.1.4.1.171.12.1.2.18.1.1.12.3 i 3",
              shell=True, stdin=PIPE, stdout=PIPE).stdout.read().split()


def get_md5_sum(gms_file_name):
    m = hashlib.md5()
    fd = open(gms_file_name, 'rb')
    b = fd.read()
    m.update(b)
    fd.close()
    return m.hexdigest()


def check_config(cc_device_id, cc_hash):
    cursor3 = db.cursor()
    cursor3.execute("SELECT hash FROM backup WHERE `devid` = '" + cc_device_id + "' ORDER BY date DESC LIMIT 1")
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
host_name = config.get('database', 'host')
user_name = config.get('database', 'user')
password = config.get('database', 'passwd')
db_name = config.get('database', 'db')

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
                    AND `devices_config`.`do_backup` = '1'")

for row in cursor.fetchall():
    file_name = row[0] + "_" + str(datetime.date.today()) + "_" + get_random_word() + ".cfg"
    do_backup_config(row[0], row[1], row[2], ip_tftp_server, file_name)

    sleep(5)

    if os.path.isfile(path_to_tftp_folder + file_name):
        md5_hash = get_md5_sum(path_to_tftp_folder + file_name)

        if check_config(str(row[3]), str(md5_hash)):
            print str(row[3]) + "Config file did not update science last time"
            remove_file(file_name)
        else:
            move_file_to_archive(file_name)
            cursor.execute("insert into backup (devid, fname, hash)\
                            VALUES(" + str(row[3]) + ", '" + str(file_name) + "', '" + str(md5_hash) + "')")
            db.commit()
            print "Config was updated..."
    else:
        print "File not found"

db.commit()
db.close()
