import yaml
import os,sys,stat
from flask import Flask
from flask import request
import logging
import logging.config

def readconfig(pathtoconfig):
    with open(pathtoconfig, 'r') as f:
        return yaml.load(f)

def set_jobdirroot(path):
    global jobdirroot
    jobdirroot = path

def get_jobdirroot():
    return jobdirroot

def create_dir(path):
    if not os.path.exists(path): os.makedirs(path)

def save_a_file(directory,name,content):
    fullpath = os.path.join(directory,name)
    fo = open(fullpath, "wb")
    fo.write(content);
    fo.close()
    return fullpath

def gen_filename_by_index(name,indexlist):
    filename = name
    for i in indexlist:
        filename = filename + "_" + str(i)
    return filename

def create_input_files(confjob,directory):
    for d in confjob['inputs']:
        filename = gen_filename_by_index(d['name'],d['index_list'])
        #filename = d['name']+"_"+str(d['index'])
        log.debug("- file to save: \""+filename+"\"")
        if os.path.exists(os.path.join(directory,filename)):
            log.warning("- file \""+filename+"\" already exists! Renaming...")
            ind = 1 
            while os.path.exists(os.path.join(directory,filename+"."+str(ind))):
                ind+=1
            filename = filename+"."+str(ind)
        save_a_file(directory, filename ,d['content'])
        log.debug("- file saved as \""+filename+"\"")

def deploy(confjob):
    wfidstr = confjob['wfid']
    log.debug("- wfid: "+wfidstr)
  
    wfiddir = os.path.join(get_jobdirroot(),wfidstr)
    if os.path.exists(wfiddir):
        log.debug("- directory already exists...")
    else:
        create_dir(wfiddir)
    create_input_files(confjob,wfiddir)
    log.info("File collection finished.")

def loadconfig(sysconfpath):
    global confsys, app, confapp, routepath, log
    confsys = readconfig(sysconfpath)
    log = logging.config.dictConfig(confsys['logging'])
    log = logging.getLogger("jobflow.collector")
    set_jobdirroot(confsys['jobdirroot-collector'])

routepath = "/jobflow"
app = Flask(__name__)
 
@app.route(routepath,methods=['POST'])
def receive():
    log.info("New file(s) arrived.")
    rdata = request.get_data()
    confjob = yaml.load(rdata)
    deploy(confjob)
    return "ok"

if len(sys.argv)==3 and sys.argv[1]=="-c":
    loadconfig(sys.argv[2])
else:
    loadconfig(os.path.join('/etc','jobflow-config-sys.yaml'))

log.info("Job directory: "+get_jobdirroot())
log.info("Listening on port "+str(confsys['listeningport-collector'])+", under url \""+routepath+"\"")

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=confsys['listeningport-collector'])




