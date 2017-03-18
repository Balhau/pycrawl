import yaml
from kafka import KafkaProducer
from kafka import KafkaConsumer
from ipwhois import IPWhois
import json
import GeoIP
from pprint import pprint

CONFIG_FILE = "config.yaml"
props=None
with open(CONFIG_FILE,'r') as f:
    props=yaml.load(f)

port_scan_source_topic = props['kafka']['topics']['portscan']
port_scan_enrich_topic = props['kafka']['topics']['enriched']
print port_scan_enrich_topic
groupid = props['kafka']['client']['groupid']
geoip_path = props['geoip']['path']

gi = GeoIP.open(geoip_path, GeoIP.GEOIP_STANDARD)

kp=KafkaProducer(bootstrap_servers=props['kafka']['hosts'])

def whoisProcessor():
    print "GroupID: ", groupid

    consumer = KafkaConsumer(port_scan_source_topic,
        group_id=groupid,
        bootstrap_servers=props['kafka']['hosts'],
        enable_auto_commit=True,
        auto_offset_reset='smallest')

    for msg in consumer:
        node=json.loads(msg.value)
        ip=str(msg.key)
        if(len(node['ports'])>0):
            print "Node: ", ip
            try:
                gir = gi.record_by_addr(ip)
                w = IPWhois(ip)
                out={}
                out['whois']=w.lookup_rdap()
                out['geoip']=gir
                message_out=json.dumps(out)
                kp.send(port_scan_enrich_topic,message_out,msg.key)
            except Exception as e:
                print "Error: %s " % e


def main():
    whoisProcessor()

if __name__ == '__main__':
    main()
