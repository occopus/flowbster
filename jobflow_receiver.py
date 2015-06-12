import yaml
import os,sys,stat
import subprocess
import uuid
from flask import Flask
from flask import request
import logging
import logging.config
import wget
import tarfile
import pwd
import glob
from ndimCollector import ndimCollector

def readconfig(pathtoconfig):
    with open(pathtoconfig, 'r') as f:
        return yaml.load(f)

def set_jobdirroot(path):
    global jobdirroot
    jobdirroot = path

def get_jobdirroot():
    return jobdirroot

def get_wfdir(wfid):
    return os.path.join(jobdirroot,wfid)

def get_inputdir(wfid):
    return os.path.join(get_wfdir(wfid),"inputs")

def get_jobdir(wfid,jobid):
    return os.path.join(jobdirroot,wfid,jobid)

def get_sandboxdir(wfid,jobid):
    jobdir = get_jobdir(wfid,jobid)
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

def download_a_file(url,targetdir):
    log.debug("- downloading "+url+"...")
    return wget.download(url,out=targetdir,bar=None)

def unzip_a_file(tgzpath,targetdir):
    tar = tarfile.open(tgzpath)
    tar.extractall(path=targetdir)
    tar.close()

def input_file_deploy(confinp,confapp,directory):
    inputlist = confapp['inputs']
    for k in inputlist:
        filename = k['name']
        if confinp['name'] == filename:
            filename=filename+"_"+str(confinp['index'])
            if 'content' in confinp:
                save_a_file(directory,filename,confinp['content'])
            elif 'tgzURL' in confinp:
                tgzpath = download_a_file(confinp['tgzURL'],directory)
                unzip_a_file(tgzpath,directory)
                untarred = os.path.join(directory,filename)
                os.chown(untarred,pwd.getpwnam('root').pw_uid,pwd.getpwnam('root').pw_gid)
            elif 'url' in confinp:
                download_a_file(confinp['url'],os.path.join(directory,filename))
            else:
                log.error("No content, nor url(s) are defined in job for file: "+filename+" !")
            log.debug("- inputfile: "+filename)

def input_files_link(inputdir,input_filenames,sandboxdir,input_names):
    for index, ifile in enumerate(input_filenames):
        os.symlink(os.path.join(inputdir,ifile),os.path.join(sandboxdir,input_names[index]))

    return

def create_executable(confapp,directory):
    filepath = save_a_file(directory,confapp['executable']['filename'],confapp['executable']['content'])
    st = os.stat(filepath)
    os.chmod(filepath, st.st_mode | stat.S_IEXEC)
    log.debug("- executable: "+confapp['executable']['filename'])

def download_executable(confapp,directory):
    tgzpath = download_a_file(confapp['executable']['tgzURL'],directory)
    log.debug("- executable downloaded: "+tgzpath)

    unzip_a_file(tgzpath,directory)
    log.debug("- executable extracted.")

    filepath = os.path.join(directory,confapp['executable']['filename'])
    st = os.stat(filepath)
    os.chmod(filepath, st.st_mode | stat.S_IEXEC)
    os.chown(filepath,pwd.getpwnam('occo').pw_uid,pwd.getpwnam('occo').pw_gid)
    log.debug("- executable: "+confapp['executable']['filename'])

def pass_to_executor(wfiddir,jobdir):
    newjobdir = "E_"+jobdir[2:]
    os.rename(os.path.join(wfiddir,jobdir),os.path.join(wfiddir,newjobdir))
    log.debug("- passed for exec: "+newjobdir)
    return

def deploy_input_descr(jobdir,descr):
    save_a_file(jobdir,"input_descr.yaml",yaml.dump(descr))
    return

def gen_input_filenames(input_descr):
    ifnames = []
    for index,item in enumerate(input_descr['names']):
        ifnames.append(item+"_"+str(input_descr['indexes'][index]))
    return ifnames

def gen_jobdir(input_descr):
    jobdir_name = "R_job"
    for index,item in enumerate(input_descr['names']):
        jobdir_name+="_"+str(input_descr['indexes'][index])
    return jobdir_name

def deploy(wfid,input_descr,confapp):
    log.info("Job deployment starts.")

    wfiddir = get_wfdir(wfid)
    log.debug("- jobid: "+input_descr['jobdir'])
    log.debug("- wfid: "+wfid)

    jobdir = os.path.join(wfiddir,input_descr['jobdir'])
    create_dir(jobdir)

    log.debug("- jobinput files: "+str(input_descr['files']))
    
    sandboxdir = os.path.join(jobdir,"sandbox")
    create_dir(sandboxdir)

    if 'content' in confapp['executable']:
        create_executable(confapp,sandboxdir)
    elif 'tgzURL' in confapp['executable']:
        download_executable(confapp,sandboxdir)
    else:
        log.critical("Application is not defined. No content, no url found!")
        sys.exit(1)

    input_files_link(get_inputdir(wfid),input_descr['files'],sandboxdir,input_descr['names'])

    deploy_input_descr(jobdir,input_descr)

    pass_to_executor(wfiddir,input_descr['jobdir'])
    
    log.info("Job deployment finished.")

def deploy_jobs(wfid,confapp):
    input_names = nDimColl.getDimNames()
    input_lengths = nDimColl.getDimLengths()
    input_indexes = nDimColl.getHitListHead()
    input_descr = {}
    input_descr['names']=input_names
    input_descr['lengths']=input_lengths
    input_descr['jobcount']=nDimColl.getMaxSize()
    while (input_indexes):
        input_descr['indexes']=input_indexes
        input_descr['files']=gen_input_filenames(input_descr)
        input_descr['jobdir']=gen_jobdir(input_descr)
        deploy(wfid,input_descr,confapp)
        nDimColl.removeHitListHead()
        input_indexes = nDimColl.getHitListHead()
    return

def loadconfig(sysconfpath):
    global confsys, app, confapp, routepath, log, nDimColl
    confsys = readconfig(sysconfpath)
    log = logging.config.dictConfig(confsys['logging'])
    log = logging.getLogger("jobflow.receiver")
    create_dir(confsys['jobdirroot'])
    set_jobdirroot(confsys['jobdirroot'])
    confapp = readconfig(confsys['appconfigpath'])
    nDimColl = ndimCollector(len(confapp['inputs']))

def input_set_default(input_item):
    if 'index' not in input_item.keys():
        input_item['index']=0
        input_item['count']=1

def input_register(input_item):
    if not nDimColl.checkDimExists(input_item['name']):
        nDimColl.addDim(input_item['name'],input_item['count'],nDimColl.getNumOfDim())
    nDimColl.addItem(input_item['name'],input_item['index'])
    return

routepath = "/jobflow"
app = Flask(__name__)
 
@app.route(routepath,methods=['POST'])
def receive():
    log.info("New input(s) arrived.")
    rdata = request.get_data()
    confjob = yaml.load(rdata)
    wfid = confjob['wfid']
    wfdir = get_wfdir(wfid)
    create_dir(wfdir)
    inputdir = get_inputdir(wfid)
    create_dir(inputdir)
    nDimColl.deserialise(os.path.join(wfdir,"nDimColl.yaml"))
    for input_item in confjob['inputs']:
        input_set_default(input_item)
        input_file_deploy(input_item,confapp,inputdir)
        input_register(input_item)
    deploy_jobs(wfid,confapp)
    nDimColl.serialise(os.path.join(wfdir,"nDimColl.yaml"))
    return wfid

if len(sys.argv)==3 and sys.argv[1]=="-c":
    loadconfig(sys.argv[2])
else:
    loadconfig(os.path.join('/etc','jobflow-config-sys.yaml'))

log.info("App config: "+confsys['appconfigpath'])
log.info("Job directory: "+get_jobdirroot())
log.info("Listening on port "+str(confsys['listeningport'])+", under url \""+routepath+"\"")

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=confsys['listeningport'])




