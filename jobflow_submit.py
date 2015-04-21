import requests
import yaml
import os,sys,stat

url = "http://192.168.153.107:6000/jobflow"
filetosend = os.path.join(sys.prefix,"etc","config-job.yaml")

def readconfig(pathtoconfig):
    with open(pathtoconfig, 'r') as f:
        return yaml.load(f)

sysconfpath = os.path.join(sys.prefix,'etc','jobflow-config-sys.yaml')
confsys = readconfig(sysconfpath)

def perform_sending_content(url,content):
    r = requests.post(url, data=yaml.dump(content))

def submit_a_job():
    perform_sending_content(url,readconfig(filetosend))


submit_a_job()

