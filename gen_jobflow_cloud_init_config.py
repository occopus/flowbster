import yaml

content_cmd="content:"

def load_base_template(path):
    with open(path, 'r') as f:
        return yaml.load(f)

def load_file(path):
    with open(path, 'r') as f:
        return f.read()


sec_base = load_base_template("gen_jobflow_cloud_init_base_template.yaml")


def replace_contents_of_files(sec_base):
    for files_to_read in sec_base['write_files']:
        if content_cmd == files_to_read["content"][0:len(content_cmd)]:
            filename = files_to_read["content"][len(content_cmd):]
            content_file=load_file(filename)
            files_to_read["content"]=content_file
    return sec_base

sec_base = replace_contents_of_files(sec_base)

print "#cloud-config"
print yaml.dump(sec_base, default_flow_style=False)

"""
sec_wf={}
sec_wf["write_files"]=[]
sec_wf["write_files"]+=[{}]
sec_wf["write_files"][0]["content"]=file_content


all_sec = {}
all_sec.update(sec_base)
all_sec.update(sec_wf)

print yaml.dump(all_sec, default_flow_style=False)
"""


"""
a=[]
b={"wf":"a"}
a+=[b]
print a
a[0]["wf2"]="aa"
print a
"""





