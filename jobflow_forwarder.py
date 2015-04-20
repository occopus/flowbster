import requests
import yaml
import os,sys,stat

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
        return False
    return True

def find_output_to_forward(jobdirroot):
    dirs = os.listdir(jobdirroot)

    found = False
    for name in dirs:
        confapppath = os.path.join(jobdirroot,name,'config-app.yaml')
        if not os.path.exists(confapppath):
            continue
        jobdir = os.path.join(jobdirroot,name)
        if not os.path.exists(os.path.join(jobdir,'retcode')):
            continue
        if os.path.exists(os.path.join(jobdir,'output-forwarded')):
            continue
        found = True
        break
    if found:
        return jobdir
    else:
        return False

def forward_outputs(jobdir):
    job_config = dict(readconfig(os.path.join(jobdir,"config-job.yaml")))
    if not job_config.has_key("wfid"):
        print "ERROR: key \'wfid\' not found in config-job.yaml"
        return False
    wfid = job_config.get("wfid")

    app_config = dict(readconfig(os.path.join(jobdir,"config-app.yaml")))
    if not app_config.has_key("outputs"):
        print "ERROR: key \'outputs\' not found in config-app.yaml"
        return False
    outputs = app_config.get("outputs")

    forward_success = True
    for ind, out in enumerate(outputs):
        if os.path.exists(os.path.join(jobdir,'output-forwarded-'+str(ind))):
            continue
       
        url = out.get("targeturl")
        if not os.path.exists(os.path.join(jobdir,'output-content-'+str(ind)+'.yaml')):
            job_dict = {}
            job_dict['wfid'] = wfid
            job_dict['inputs'] = []
            one_input = {}
            one_input['name'] = out.get("targetname")
            with open(os.path.join(jobdir,"sandbox",out.get("name")), 'r') as fo:
                out_content = fo.read()
            one_input['content'] = out_content
            job_dict['inputs'].append(one_input)
            content = yaml.dump(job_dict,default_flow_style=False)
            save_a_file(jobdir,'output-content-'+str(ind)+'.yaml',content)
            save_a_file(jobdir,'output-url-'+str(ind)+'.txt',url)
          
        print "Sending content for \""+out.get("targetname")+"\" to \""+url+"\""
        content = dict(readconfig(os.path.join(jobdir,'output-content-'+str(ind)+'.yaml')))
        success = perform_sending_content(url,content)
        if success:
            save_a_file(jobdir,'output-forwarded-'+str(ind),'done')
            print "Sending: SUCCESS."
        else:
            print "Sending: FAILED. Will retry later."
            forward_success = False
    if forward_success:
        save_a_file(jobdir,'output-forwarded','done')
        
    return True



def forward_one_output():
    print "Looking for an output to be forwarded at \""+jobdirroot+"\""
    jobdir = find_output_to_forward(jobdirroot)
    if jobdir:
        print "Found output to forward at \""+jobdir+"\""
        forward_outputs(jobdir)
        print "Forward finished."
        return jobdir
    else:
        print "No output found to be forwarded."
        return False


url = "http://192.168.153.107:5000/jobflow"
filetosend = "config-job.yaml"

sysconfpath = os.path.join('config-sys.yaml')
confsys = dict(readconfig(sysconfpath))
jobdirroot = confsys['jobdirroot']

forward_one_output()

