from flask import Flask
import yaml
import jobflow_submit
import uuid
import os

app = Flask(__name__)

def readconfig(pathtoconfig):
    with open(pathtoconfig, 'r') as f:
        return yaml.load(f)

sysconfpath = os.path.join('config-sys.yaml')
confsys = dict(readconfig(sysconfpath))
jobflow_submit.set_jobdirroot(confsys['jobdirroot'])

confjob = dict(readconfig('config-job.yaml'))
confapp = dict(readconfig('config-app.yaml'))

@app.route("/jobflow")
def submit():
    jobid = str(uuid.uuid1())
    jobflow_submit.submit(jobid,confjob,confapp)
    return jobid

if __name__ == "__main__":
    app.run(host='0.0.0.0')

#submit()


