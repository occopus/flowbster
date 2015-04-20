import requests
import yaml
import os,sys,stat

url = "http://192.168.153.107:5000/jobflow"
filetosend = "config-job.yaml"

def readconfig(pathtoconfig):
    with open(pathtoconfig, 'r') as f:
        return yaml.load(f)

def save_a_file(directory,name,content):
    fullpath = os.path.join(directory,name)
    fo = open(fullpath, "wb")
    fo.write(content);
    fo.close()
    return fullpath

sysconfpath = os.path.join('config-sys.yaml')
confsys = dict(readconfig(sysconfpath))
jobdirroot = confsys['jobdirroot']

def perform_sending_content(url,content):
    r = requests.post(url, data=yaml.dump(content))

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
        if os.path.exists(os.path.join(jobdir,'forwarded')):
            continue
        found = True
        break
    if found:
        return jobdir
    else:
        return False

def perform_forward(jobdir):


    save_a_file(jobdir,'forwarded','done')
    return


def forward_one_output():
    print "Looking for an output to be forwarded at \""+jobdirroot+"\""
    jobdir = find_output_to_forward(jobdirroot)
    if jobdir:
        print "Found output to forward at \""+jobdir+"\""
        perform_forward(jobdir)
        print "Forward done."
        return jobdir
    else:
        print "No output found to be executed."
        return False

def test_forward():
    perform_sending_content(url,dict(readconfig(filetosend)))


forward_one_output()
#test_forward()

