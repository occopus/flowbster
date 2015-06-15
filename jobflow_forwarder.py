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
    
    forward_success = True
    for ind, out in enumerate(outputs):
        
        genfilename = "genfiles-"+out["name"]+".yaml"
        log.debug("Checking generated files for \""+out["name"]+"\"")
        if os.path.exists(os.path.join(jobdir,genfilename)):
            log.debug("Skipping creating sum of generated files for \""+out["name"]+"\"")
            genfiles = readconfig(os.path.join(jobdir,genfilename))
        else:
            fullpath = os.path.join(jobdir,"sandbox",out["name"])
            generated_files = glob.glob(fullpath)
            genfiles={}
            genfiles['count'] = len(generated_files)
            genfiles['files'] = [ {"ind":ind,"name":os.path.basename(x)} for ind,x in enumerate(generated_files) ]
            save_a_file(jobdir,genfilename,yaml.dump(genfiles,default_flow_style=False))

        
        for genfiles_ind, one_genfile in enumerate(genfiles):
            """log.debug("Checking output: \""+out["name"]+"\"")
            if os.path.exists(os.path.join(jobdir,'output-forwarded-'+str(ind))):
                log.debug("Output \""+out["name"]+"\" has already been forwarded as \""+out["targetname"]+"\"")
                continue
        """
            if genfiles_ind < genfiles['done']
                continue
       
            job_dict = {}   
            job_dict['wfid'] = inputs['wfid']
            job_dict['inputs'] = []
            one_input = {}
            one_input['name'] = out["targetname"]
            one_input['index'] = genfiles_ind
            one_input['count'] = genfiles['count']
            with open(os.path.join(jobdir,"sandbox",one_genfile), 'r') as fo:
                one_input['content'] = fo.read()
            job_dict['inputs'].append(one_input)
            content = yaml.dump(job_dict,default_flow_style=False)
            url = out["targeturl"]
          
            log.info("Sending content for \""+out.get("targetname")+"\" to \""+url+"\"")
            success = perform_sending_content(url,content)
            if success:
                genfiles['done']+=1
                save_a_file(jobdir,'output-forwarded-'+str(ind),'done')
                log.info("Sending: SUCCESS.")
            else:
                log.info("Sending: FAILED. Will retry later.")
                forward_success = False
                break
    if forward_success:
        save_a_file(jobdir,'output-forwarded','done')
        
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

