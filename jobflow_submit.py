import yaml
import os,sys,stat
import subprocess
import uuid

import jobflow_exec

sysconfpath = os.path.join('config-sys.yaml')

def readconfig(pathtoconfig):
    with open(pathtoconfig, 'r') as f:
        return yaml.load(f)

def get_jobdirroot(config):
    return config['jobdirroot']

def get_exe_name(config):
    return config['executable']['filename']

def get_args(config):
    return config['arguments']

def get_sandboxdir(jobdir):
    return os.path.join(jobdir,'sandbox')

def create_dir(path):
    if not os.path.exists(path): os.makedirs(path)

confsys = dict(readconfig(sysconfpath))
jobdirroot = get_jobdirroot(confsys)

def submit(jobid,confjob,confapp):
    jobdir =  os.path.join(jobdirroot,jobid)
    create_dir(jobdir)

    fw = open(os.path.join(jobdir,"config-job.yaml"), "wb")
    fw.write(yaml.dump(confjob));
    fw.close()

    fw = open(os.path.join(jobdir,"config-app.yaml"), "wb")
    fw.write(yaml.dump(confapp));
    fw.close()

    sandboxdir = get_sandboxdir(jobdir)
    create_dir(sandboxdir)

    exename = get_exe_name(confapp)
    arguments = get_args(confapp)

    create_dir(sandboxdir)
    jobflow_exec.create_input_files(confjob,confapp,sandboxdir)
    jobflow_exec.create_executable(confapp,sandboxdir)
    jobflow_exec.perform_exec(sandboxdir,exename,arguments)

jobid = str(uuid.uuid1())
confjob = dict(readconfig('config-job.yaml'))
confapp = dict(readconfig('config-app.yaml'))

submit(jobid,confjob,confapp)



