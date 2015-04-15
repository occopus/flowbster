import yaml
import os,sys,stat
import subprocess

def save_a_file(directory,name,content):
    fullpath = os.path.join(directory,name)
    fo = open(fullpath, "wb")
    fo.write(content);
    fo.close()
    return fullpath

def create_input_files(confjob,confapp,directory):
    inputlist = confapp['inputs']
    for k in inputlist:
        filename = k['name']
        for d in confjob['inputs']:
            if d['name'] == filename:
                save_a_file(directory,filename,d['content'])

def create_executable(confapp,directory):
    filepath = save_a_file(directory,confapp['executable']['filename'],confapp['executable']['content'])
    st = os.stat(filepath)
    os.chmod(filepath, st.st_mode | stat.S_IEXEC)

def perform_exec(sandboxdir,exename,arguments):
    os.chdir(sandboxdir)
    status = subprocess.call('./'+exename+' '+arguments+'>../stdout 2>../stderr',shell=True)
    save_a_file('..','retcode',str(status))



