import yaml
import os,sys,stat
import subprocess
import logging
import logging.config
import time

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
    log.info("Executing \""+exename+' '+arguments+'>../stdout 2>../stderr')
    status = subprocess.call('./'+exename+' '+arguments+'>../stdout 2>../stderr',shell=True)
    save_a_file('..','retcode',str(status))

def find_job_to_run(jobdirroot):
    dirs = os.listdir(jobdirroot)
    for name in dirs:
        found = True
        confapppath = os.path.join(jobdirroot,name,'config-app.yaml')
        if not os.path.exists(confapppath):
            log.debug("Cannot find file: \""+confapppath+"\". Ignoring directory.")
            continue

        log.debug("Examining directory: \""+os.path.join(jobdirroot,name)+"\"")
        if os.path.exists(os.path.join(jobdirroot,name,'retcode')):
            log.debug("\"retcode\" found. Nothing to be executed. Skipping...")
            continue

        confapp = readconfig(confapppath)
        inputlist = confapp['inputs']
        for k in inputlist:
            inputfilepath = os.path.join(jobdirroot,name,"sandbox",k['name'])
            if not os.path.exists(inputfilepath):
                log.debug("Input file \""+inputfilepath+"\" is still missing. Skipping...")
                found = False

        if found:
            exename = confapp['executable']['filename']
            arguments = confapp['arguments']
            return (os.path.join(jobdirroot,name),exename,arguments)
    return (False,False,False)

def exec_one_job():
    log.info("Looking for a job to be executed at \""+jobdirroot+"\"")
    (jobdir,exename,arguments) = find_job_to_run(jobdirroot)
    if jobdir:
        log.info("Found job to execute at \""+jobdir+"\"")
        sandboxdir = os.path.join(jobdir,'sandbox')
        perform_exec(sandboxdir,exename,arguments)
        log.info("Execution done.")
        return jobdir
    else:
        log.info("No job found to be executed.")
        return False



def loadconfig(sysconfpath):
    global confsys, jobdirroot, log
    confsys = readconfig(sysconfpath)
    jobdirroot = os.path.join(confsys['jobdirroot'])
    if not os.path.exists(jobdirroot): os.makedirs(jobdirroot)
    logging.config.dictConfig(confsys['logging'])
    log = logging.getLogger("jobflow.executor")

if len(sys.argv)==3 and sys.argv[1]=="-c":
    loadconfig(sys.argv[2])
else:
    loadconfig(os.path.join('/etc','jobflow-config-sys.yaml'))

while True:
    exec_one_job()
    time.sleep(confsys['sleepinterval'])











