import yaml
import os,sys,stat
import subprocess
import uuid

import jobflow_exec

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

def deploy(jobid,confjob,confapp):
    jobdir = get_jobdir(jobid)
    create_dir(jobdir)

    fw = open(os.path.join(jobdir,"config-job.yaml"), "wb")
    fw.write(yaml.dump(confjob));
    fw.close()

    fw = open(os.path.join(jobdir,"config-app.yaml"), "wb")
    fw.write(yaml.dump(confapp));
    fw.close()

    sandboxdir = get_sandboxdir(jobid)
    create_dir(sandboxdir)

def execute(jobid,confjob,confapp):
    sandboxdir = get_sandboxdir(jobid)
    jobflow_exec.create_input_files(confjob,confapp,sandboxdir)
    jobflow_exec.create_executable(confapp,sandboxdir)
    
    exename = get_exe_name(confapp)
    arguments = get_args(confapp)
    jobflow_exec.perform_exec(sandboxdir,exename,arguments)

def submit(jobid,confjob,confapp):
    deploy(jobid,confjob,confapp)
    execute(jobid,confjob,confapp)



