import requests
import yaml
import os,sys,stat
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

def perform_sending_content(url,content):
    try:
        r = requests.post(url, data=yaml.dump(content))
    except:
        log.exception('')
        return False
    return True

def find_output_to_forward(jobdirroot):
    dirs = glob.glob(os.path.join(jobdirroot,"*/F_*"))
    if dirs:
        return dirs[0]
    else:
        return False

def mark_job_as_forwarded(jobdir):
    wfdir = os.path.dirname(jobdir)
    jobdirname = os.path.basename(jobdir)
    newjobdir = "D_"+jobdirname[2:]
    os.rename(jobdir,os.path.join(wfdir,newjobdir))
    return newjobdir

def forward_outputs(jobdir):
    inputs = readconfig(os.path.join(jobdir,"inputs.yaml"))
    outputs = confapp["outputs"]
    
    forward_finished = True
    for ind, out in enumerate(outputs):
        
        genfilename = "genfiles-"+out["name"]+".yaml"
        if os.path.exists(os.path.join(jobdir,genfilename)):
            log.debug("Loading list of generated files for \""+out["name"]+"\"")
            genfiles = readconfig(os.path.join(jobdir,genfilename))
        else:
            log.debug("Creating list of generated files for \""+out["name"]+"\"")
            fullpath = os.path.join(jobdir,"sandbox",out["name"])
            generated_files = glob.glob(fullpath)
            genfiles = {}
            genfiles['count'] = len(generated_files)
            genfiles['files'] = [ {"index":ind,"name":os.path.basename(x)} for ind,x in enumerate(generated_files) ]
            save_a_file(jobdir,genfilename,yaml.dump(genfiles,default_flow_style=False))
        log.debug("Num of generated files for \""+out["name"]+"\" is "+str(genfiles['count']))

        target_forward_count_filename = os.path.join(jobdir,'target-forward-count-'+str(ind))
        if os.path.exists(target_forward_count_filename):
            target_forward = readconfig(target_forward_count_filename)
        else:
            target_forward = {}
            target_forward['count'] = 0
            save_a_file(jobdir,target_forward_count_filename,yaml.dump(target_forward,default_flow_style=False))
        log.debug("Target forward count for link "+str(ind)+" is "+str(target_forward['count']))

        for one_genfile in genfiles['files']:
            log.debug("Preparing sending "+str(one_genfile)+" to link "+str(ind))
            """log.debug("Checking output: \""+out["name"]+"\"")
            if os.path.exists(os.path.join(jobdir,'output-forwarded-'+str(ind))):
                log.debug("Output \""+out["name"]+"\" has already been forwarded as \""+out["targetname"]+"\"")
                continue
        """
            if one_genfile['index'] < target_forward['count']:
                continue
       
            content = {}   
            content['wfid'] = str(inputs['wfid'])
            content['inputs'] = []
            one_input = {}
            one_input['name'] = out["targetname"]
            one_input['index'] = one_genfile['index']
            one_input['count'] = genfiles['count']
            with open(os.path.join(jobdir,"sandbox",one_genfile['name']), 'r') as fo:
                one_input['content'] = fo.read()
            content['inputs'].append(one_input)
            url = out["targeturl"]
          
            log.info("Sending content for \""+out.get("targetname")+"\" to \""+url+"\"")
            log.debug("Content is: \n"+str(content))
            success = perform_sending_content(url,content)
            if success:
                target_forward['count']+=1
                save_a_file(jobdir,target_forward_count_filename,yaml.dump(target_forward,default_flow_style=False))
                log.info("Sending: SUCCESS.")
            else:
                log.info("Sending: FAILED. Will retry later.")
                forward_finished = False
                break
    if forward_finished:
        mark_job_as_forwarded(jobdir)
        
    return True



def forward_one_output():
    log.info("Looking for an output to be forwarded at \""+jobdirroot+"\"")
    jobdir = find_output_to_forward(jobdirroot)
    if jobdir:
        log.info("Found output to forward at \""+jobdir+"\"")
        forward_outputs(jobdir)
        log.info("Forward finished.")
        return False
    else:
        log.info("No output found to be forwarded.")
        return False


def loadconfig(sysconfpath):
    global confsys, jobdirroot, log, confapp
    confsys = readconfig(sysconfpath)
    jobdirroot = os.path.join(confsys['jobdirroot'])
    if not os.path.exists(jobdirroot): os.makedirs(jobdirroot)
    logging.config.dictConfig(confsys['logging'])
    log = logging.getLogger("jobflow.forwarder")
    confapp = readconfig(confsys['appconfigpath'])


if len(sys.argv)==3 and sys.argv[1]=="-c":
    loadconfig(sys.argv[2])
else:
    loadconfig(os.path.join('/etc','jobflow-config-sys.yaml'))

while True:
    if forward_one_output()==False :
        time.sleep(confsys['sleepinterval'])

