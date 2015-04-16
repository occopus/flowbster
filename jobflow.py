from flask import Flask
import yaml
import jobflow_submit
import uuid
import os

routepath = "/jobflow"
app = Flask(__name__)

def readconfig(pathtoconfig):
    with open(pathtoconfig, 'r') as f:
        return yaml.load(f)

sysconfpath = os.path.join('config-sys.yaml')
confsys = dict(readconfig(sysconfpath))
jobflow_submit.set_jobdirroot(confsys['jobdirroot'])

confjob = dict(readconfig('config-job.yaml'))
confapp = dict(readconfig('config-app.yaml'))

print "Listening on port 5000, under url \""+routepath+"\""
print "Job dir: "+jobflow_submit.get_jobdirroot()

@app.route(routepath)
def submit():
    jobid = jobflow_submit.get_jobid_by_wfid(confjob)
    jobflow_submit.submit(jobid,confjob,confapp)
    print jobid
    return jobid

if __name__ == "__main__":
    app.run(host='0.0.0.0')

#submit()
#print jobflow_submit.get_jobid_by_wfid(confjob)



