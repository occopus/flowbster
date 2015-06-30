import yaml
import os,sys,stat
import subprocess
import logging
import logging.config
import time
import glob

def readconfig(pathtoconfig):
    with open(pathtoconfig, 'r') as f:
        return yaml.load(f)

def save_a_file(directory,name,content):
    fullpath = os.path.join(directory,name)
    fo = open(fullpath, "wb")
    fo.write(content);
    fo.close()
    return fullpath

def perform_exec(sandboxdir,exename,arguments):
    os.chdir(sandboxdir)
    command = "./"+exename+" "+arguments+" >../stdout 2>../stderr"
    log.info(" - run: \""+command+"\"")
    status = subprocess.call(command,shell=True)
    save_a_file('..','retcode',str(status))

def find_job_to_run(jobdirroot):
    dirs = glob.glob(os.path.join(jobdirroot,"*/E_*"))
    if dirs:
        jobdir = dirs[0]
        exename = confapp['executable']['filename']
        arguments = confapp['arguments']
        return (jobdir,exename,arguments)
    else:
        return (False,False,False)

def pass_to_forwarder(jobdir):
    wfdir = os.path.dirname(jobdir)
    jobdirname = os.path.basename(jobdir)
    newjobdir = "F_"+jobdirname[2:]
    os.rename(jobdir,os.path.join(wfdir,newjobdir))
    return newjobdir

def exec_one_job():
    log.info("Looking for a job to be executed at \""+jobdirroot+"\"")
    (jobdir,exename,arguments) = find_job_to_run(jobdirroot)
    if jobdir:
        log.info("NEW JOB to execute at \""+jobdir+"\"")
        log.debug(" - exe: "+exename)
        log.debug(" - args: "+arguments)
        sandboxdir = os.path.join(jobdir,'sandbox')
        perform_exec(sandboxdir,exename,arguments)
        jobdir = pass_to_forwarder(jobdir)
        log.info("DONE. New dir is \""+jobdir+"\".")
        return jobdir
    else:
        log.info("No job found to be executed.")
        return False

def loadconfig(sysconfpath):
    global confsys, jobdirroot, log, confapp
    confsys = readconfig(sysconfpath)
    jobdirroot = os.path.join(confsys['jobdirroot'])
    if not os.path.exists(jobdirroot): os.makedirs(jobdirroot)
    logging.config.dictConfig(confsys['logging'])
    log = logging.getLogger("jobflow.executor")
    confapp = readconfig(confsys['appconfigpath'])

if len(sys.argv)==3 and sys.argv[1]=="-c":
    loadconfig(sys.argv[2])
else:
    loadconfig(os.path.join('/etc','jobflow-config-sys.yaml'))

while True:
    try:
        if exec_one_job()==False:
            time.sleep(confsys['sleepinterval']) 
    except BaseException:
        log.exception("EXCEPTION:")

