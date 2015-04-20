import yaml
import os,sys,stat
import subprocess
import uuid
from flask import Flask
from flask import request

def readconfig(pathtoconfig):
    with open(pathtoconfig, 'r') as f:
        return yaml.load(f)

def set_jobdirroot(path):
    global jobdirroot
    jobdirroot = path

sysconfpath = os.path.join('config-sys.yaml')
confsys = dict(readconfig(sysconfpath))
set_jobdirroot(confsys['jobdirroot'])

confjob = dict(readconfig('config-job.yaml'))
confapp = dict(readconfig('config-app.yaml'))

routepath = "/jobflow"
app = Flask(__name__)

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

def create_executable(confapp,directory):
    filepath = save_a_file(directory,confapp['executable']['filename'],confapp['executable']['content'])
    st = os.stat(filepath)
    os.chmod(filepath, st.st_mode | stat.S_IEXEC)

def get_jobid_by_wfid(confjob):
    #search through existing jobs directories
    jobid = str(uuid.uuid1())
    wfidstr=confjob['wfid']
    jobdirroot=get_jobdirroot()
    dirs = os.listdir(jobdirroot)
    for name in dirs:
       wfidfile = os.path.join(jobdirroot,name,'wfid='+wfidstr)
       if os.path.exists(wfidfile):
           jobid = name

    return jobid

def deploy(jobid,confjob,confapp):
    jobdir = get_jobdir(jobid)
    create_dir(jobdir)
    wfidstr = confjob['wfid']
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
    
    fw = open(os.path.join(jobdir,"config-app.yaml"), "wb")
    fw.write(yaml.dump(confapp));
    fw.close()
    sandboxdir = get_sandboxdir(jobid)
    create_dir(sandboxdir)
    create_executable(confapp,sandboxdir)
    create_input_files(confjob,confapp,sandboxdir)
   
@app.route(routepath,methods=['POST'])
def receive():

    rdata = request.get_data()
    print "aaa"
    confjob = dict(yaml.load(rdata))
    print str(confjob)
    jobid = get_jobid_by_wfid(confjob)
    print jobid
    deploy(jobid,confjob,confapp)
    print jobid
    return jobid


print "Listening on port 5000, under url \""+routepath+"\""
print "Job dir: "+get_jobdirroot()

if __name__ == "__main__":
    app.run(host='0.0.0.0')




