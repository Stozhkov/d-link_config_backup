import os
import MySQLdb
import hashlib
import datetime
import ConfigParser
from subprocess import Popen, PIPE


def do_backup_config(ip, community, type, tftp, file_name):
    if type in [17, 25]:
        Popen("snmpset -v2c -c " + community + " " + ip + " 1.3.6.1.4.1.171.12.1.2.1.1.3.3 a " + tftp + " \
            1.3.6.1.4.1.171.12.1.2.1.1.4.3 i 2 \
            1.3.6.1.4.1.171.12.1.2.1.1.5.3 s dlink/" + file_name + " \
            1.3.6.1.4.1.171.12.1.2.1.1.7.3 i 2 \
            1.3.6.1.4.1.171.12.1.2.1.1.8.3 i 3",
              shell=True, stdin=PIPE, stdout=PIPE).stdout.read().split()
    else:
        Popen("snmpset -v2c -c " + community + " " + ip + " 1.3.6.1.4.1.171.12.1.2.18.1.1.3.3 a " + tftp + " \
            1.3.6.1.4.1.171.12.1.2.18.1.1.5.3 s dlink/" + file_name + " \
            1.3.6.1.4.1.171.12.1.2.18.1.1.8.3 i 2 \
            1.3.6.1.4.1.171.12.1.2.18.1.1.12.3 i 3",
              shell=True, stdin=PIPE, stdout=PIPE).stdout.read().split()


def get_md5_sum(file_name):
    m = hashlib.md5()
    fd = open(file_name, 'rb')
    b = fd.read()
    m.update(b)
    fd.close()
    return m.hexdigest()


#def check_config(devid, hash):



config = ConfigParser.ConfigParser()
config.read('config.cfg')

db = MySQLdb.connect(host=config.get('database', 'host'),
                     user=config.get('database', 'user'),
                     passwd=config.get('database', 'passwd'),
                     db=config.get('database', 'db'))
ip_tftp_server = config.get('tftp', 'ip')
path_to_tftp_folder = config.get('tftp', 'path_to_tftp_folder')

cursor = db.cursor()

cursor.execute("select ip, access_snmp_write, type, id from devices LIMIT 10")

for row in cursor.fetchall():
    file_name = row[0] + "_" + str(datetime.date.today()) + ".cfg"
    do_backup_config(row[0], row[1], row[2], ip_tftp_server, file_name)

    if os.path.isfile(path_to_tftp_folder + file_name):
        md5_hash = get_md5_sum(path_to_tftp_folder + file_name)
        print md5_hash
        print file_name

        cursor.execute("insert into backup (devid, fname, hash) VALUES(" + str(row[3]) + ", '" + str(file_name) + "', '" + str(md5_hash) + "')")
        db.commit()
    else:
        print "File not found"

db.commit()
db.close()
