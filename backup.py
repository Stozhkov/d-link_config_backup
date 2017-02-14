import MySQLdb
import datetime
import ConfigParser
from subprocess import Popen, PIPE


def do_backup_config(ip, community, type, tftp):
    if type in [17, 25]:
        Popen("snmpset -v2c -c " + community + " " + ip + " 1.3.6.1.4.1.171.12.1.2.1.1.3.3 a " + tftp + " \
            1.3.6.1.4.1.171.12.1.2.1.1.4.3 i 2 \
            1.3.6.1.4.1.171.12.1.2.1.1.5.3 s dlink/" + ip + "_" + str(datetime.date.today()) + ".cfg \
            1.3.6.1.4.1.171.12.1.2.1.1.7.3 i 2 \
            1.3.6.1.4.1.171.12.1.2.1.1.8.3 i 3",
              shell=True, stdin=PIPE, stdout=PIPE).stdout.read().split()
    else:
        Popen("snmpset -v2c -c " + community + " " + ip + " 1.3.6.1.4.1.171.12.1.2.18.1.1.3.3 a " + tftp + " \
            1.3.6.1.4.1.171.12.1.2.18.1.1.5.3 s dlink/" + ip + "_" + str(datetime.date.today()) + ".cfg \
            1.3.6.1.4.1.171.12.1.2.18.1.1.8.3 i 2 \
            1.3.6.1.4.1.171.12.1.2.18.1.1.12.3 i 3",
              shell=True, stdin=PIPE, stdout=PIPE).stdout.read().split()


config = ConfigParser.ConfigParser()
config.read('config.cfg')

db = MySQLdb.connect(host=config.get('database', 'host'),
                     user=config.get('database', 'user'),
                     passwd=config.get('database', 'passwd'),
                     db=config.get('database', 'db'))
ip_tftp_server = config.get('tftp', 'ip')

cursor = db.cursor()

cursor.execute("select ip, access_snmp_write, type from devices LIMIT 10")

for row in cursor.fetchall():
#    print row[0]; print row[1]; print row[2]
    do_backup_config(row[0], row[1], row[2], ip_tftp_server)

db.close()
