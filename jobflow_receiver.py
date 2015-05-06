import yaml
import os,sys,stat
import subprocess
import uuid
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

def get_jobdir(jobid):
    return os.path.join(jobdirroot,jobid)

def get_sandboxdir(jobid):
    jobdir = get_jobdir(jobid)
    return os.path.join(jobdir,'sandbox')

def get_exe_name(config):
    return config['executable']['filename']

def get_args(config):
    return config['arguments']

def create_dir(path):
    if not os.path.exists(path): os.makedirs(path)

def save_a_file(directory,name,content):
    fullpath = os.path.join(directory,name)
    fo = open(fullpath, "wb")
    fo.write(content);
    fo.close()
    return fullpath

def create_input_files(confjob,confapp,directory):
    inputlist = confapp['inputs']
    for k in inputlist:
        filename = k['name']
        for d in confjob['inputs']:
            if d['name'] == filename:
                save_a_file(directory,filename,d['content'])
                log.debug("- inputfile: "+filename)

def create_executable(confapp,directory):
    filepath = save_a_file(directory,confapp['executable']['filename'],confapp['executable']['content'])
    st = os.stat(filepath)
    os.chmod(filepath, st.st_mode | stat.S_IEXEC)
    log.debug("- executable: "+confapp['executable']['filename'])

def get_jobid_by_wfid(confjob):
    jobid = str(uuid.uuid1())
    wfidstr=confjob['wfid']
    jobdirroot=get_jobdirroot()
    dirs = os.listdir(jobdirroot)
    for name in dirs:
       wfidfile = os.path.join(jobdirroot,name,'wfid='+wfidstr)
       if os.path.exists(wfidfile):
           return name
    return jobid

def deploy(jobid,confjob,confapp):
    jobdir = get_jobdir(jobid)
    create_dir(jobdir)
    wfidstr = confjob['wfid']
    log.debug("- wfid: "+wfidstr)
    fw = open(os.path.join(jobdir,"wfid="+wfidstr), "wb")
    fw.write(wfidstr);
    fw.close()
  
    confjobname="config-job.yaml"
    if os.path.exists(os.path.join(jobdir,confjobname)):
        ind=1
        while os.path.exists(os.path.join(jobdir,confjobname+"."+str(ind))):
            ind=ind+1
        confjobname=confjobname+"."+str(ind)
    fw = open(os.path.join(jobdir,confjobname), "wb")
    fw.write(yaml.dump(confjob));
    fw.close()
    log.debug("- jobconfig file: "+confjobname)
    
    fw = open(os.path.join(jobdir,"config-app.yaml"), "wb")
    fw.write(yaml.dump(confapp));
    fw.close()
    sandboxdir = get_sandboxdir(jobid)
    create_dir(sandboxdir)
    create_executable(confapp,sandboxdir)
    create_input_files(confjob,confapp,sandboxdir)
    log.info("Job deployment finished.")

def loadconfig():
    global confsys, app, confapp, routepath, log
    sysconfpath = os.path.join('/etc','jobflow-config-sys.yaml')
    confsys = readconfig(sysconfpath)
    log = logging.config.dictConfig(confsys['logging'])
    log = logging.getLogger("jobflow.receiver")
    set_jobdirroot(os.path.join(sys.prefix,confsys['jobdirroot']))
    confapp = readconfig(confsys['appconfigpath'])

routepath = "/jobflow"
app = Flask(__name__)
 
@app.route(routepath,methods=['POST'])
def receive():
    log.info("New job arrived.")
    rdata = request.get_data()
    confjob = yaml.load(rdata)
    jobid = get_jobid_by_wfid(confjob)
    log.info("Assigned jobid is \""+jobid+"\"")
    deploy(jobid,confjob,confapp)
    return jobid

loadconfig()
log.info("App config: "+os.path.join(sys.prefix,confsys['appconfigpath']))
log.info("Job directory: "+get_jobdirroot())
log.info("Listening on port "+str(confsys['listeningport'])+", under url \""+routepath+"\"")

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=confsys['listeningport'])




