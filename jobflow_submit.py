import requests
import yaml
import sys

def printhelp():
    print "Usage: jobflow_submitter [file] [url]"
    print "  file: containing jobflow definition"
    print "  url : endpoint of a jobflow_receiver component"

def parse_arguments():
    if len(sys.argv)!=3:
        print "Wrong number of arguments!"
        printhelp()
        return (False,False)
    return (sys.argv[1],sys.argv[2])


(path,url) = parse_arguments()
if path:
    try:
        file = open(path,'r')
        content = yaml.load(file)
    except Exception as e:
        print "Error when reading file: %s" % e
        sys.exit(1)
            
    try:
        requests.post(url, data=yaml.dump(content))
    except requests.exceptions.RequestException as e:
        print "Error when posting message: %s" % e
        sys.exit(1)

