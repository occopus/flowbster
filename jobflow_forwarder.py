import requests
import yaml
import uuid
import os,sys,stat
import logging
import logging.config
import time
import glob
import random

def readconfig(pathtoconfig):
    with open(pathtoconfig, 'r') as f:
        return yaml.load(f)

def save_a_file(directory,name,content):
    fullpath = os.path.join(directory,name)
    fo = open(fullpath, "wb")
    fo.write(content);
    fo.close()
    return fullpath

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
            if "filter" in out:
                fullpath = os.path.join(jobdir,"sandbox",out["filter"])
            else:
                fullpath = os.path.join(jobdir,"sandbox",out["name"])
            log.debug("Filter is: \""+fullpath+"\"")
            generated_files = glob.glob(fullpath)
            generated_files.sort()
            genfiles = {}
            genfiles['count'] = len(generated_files)
            genfiles['files'] = [ {"index":outind,"name":os.path.basename(x)} for outind,x in enumerate(generated_files) ]
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

        if os.path.exists(os.path.join(jobdir,'inputs.yaml')):
            inputsyaml = readconfig(os.path.join(jobdir,'inputs.yaml'))
            index_list = inputsyaml['indexes']['out_file_indxs']
            count_list = inputsyaml['indexes']['out_file_maxs']
        else:
            index_list = [0]
            count_list = [1]

        log.debug("Index list: "+str(index_list))
        log.debug("Count list: "+str(count_list))
        log.debug("Genfiles: "+str(genfiles))

        for one_genfile in genfiles['files']:
            if one_genfile['index'] < target_forward['count']:
                continue

            log.debug("Preparing sending "+str(one_genfile)+" to link "+str(ind))
            content = {}   
            content['wfid'] = str(inputs['wfid'])
            content['inputs'] = []
            one_input = {}
            one_input['name'] = out["targetname"]

            if genfiles['count'] > 1:
                one_input['index_list'] = index_list+[one_genfile['index']]
                one_input['count_list'] = count_list+[genfiles['count']]
            else:
                one_input['index_list'] = index_list
                one_input['count_list'] = count_list

            itemcount=1
            for i in range(len(one_input['count_list'])):
                itemcount=itemcount*one_input['count_list'][i]

            multiplier = 1
            itemindex = 0
            for i in range(len(one_input['index_list'])-1,-1,-1):
                itemindex =  itemindex + one_input['index_list'][i] * multiplier
                multiplier = multiplier * one_input['count_list'][i]

            one_input['index'] = itemindex
            one_input['count'] = itemcount
            one_input['post_file'] = out['targetname']
            content['inputs'].append(one_input)
            r = out['targetip']
            targetiplist = [x.encode('ascii', 'ignore').split("'")[1] for x in r]
            if 'distribution' in out:
                distr = out['distribution']
                if 'random' == distr:
                    targetiplist = [targetiplist[random.randint(0, len(targetiplist)-1)]]
            log.info('Will send file to ips: {}'.format(targetiplist))
            log.debug("Content is: \n"+str(content))

            for targetip in targetiplist:
                try:
                    url = 'http://' + targetip + ':' + str(out['targetport']) + '/jobflow'
                    log.info("Sending content for \""+out.get("targetname")+"\" to \""+url+"\"")
                    yaml_id = str(uuid.uuid4())
                    payload = {'yaml': yaml_id}
                    files = {out["targetname"]: open(os.path.join(jobdir,"sandbox",one_genfile['name']), 'rb'), yaml_id: yaml.dump(content)}
                    r = requests.post(url, params=payload, files=files)
                except:
                    log.exception('')
                    log.info("Sending: FAILED. Will retry later.")
                    forward_finished = False
                    break
            target_forward['count']+=1
            save_a_file(jobdir,target_forward_count_filename,yaml.dump(target_forward,default_flow_style=False))
            log.info("Sending: SUCCESS.")
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
        return True
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
