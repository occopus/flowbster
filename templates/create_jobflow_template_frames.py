import yaml
import os
import argparse

content_cmd="content:"
script_dir=""
base_template_name="template_jobflow_sys_base.yaml"
result_file=""

def load_base_template(path):
    with open(path, 'r') as f:
        return yaml.load(f)

def load_file(path):
    with open(os.path.join(script_dir,path), 'r') as f:
        return f.read()

def replace_contents_of_files(sec_base):
    for files_to_read in sec_base['write_files']:
        if content_cmd == files_to_read["content"][0:len(content_cmd)]:
            filename = files_to_read["content"][len(content_cmd):]
            content_file=load_file(filename)
            files_to_read["content"]=content_file
    return sec_base

parser = argparse.ArgumentParser(description='Create jobflow sys base template containing the jobflow scripts.')
parser.add_argument('--base', help='specifies the base sys template without scripts')
parser.add_argument('--scriptdir', help='specifies the directory containing the jobflow scripts')
parser.add_argument('--outfile', help='specifies the file where the template is written.')
args = parser.parse_args()

if args.base is not None:
    base_template_name=args.base
if args.scriptdir is not None:
    script_dir=args.scriptdir
if args.outfile is not None:
    result_file=args.outfile

sec_base = load_base_template(base_template_name)
sec_base = replace_contents_of_files(sec_base)

result = "#cloud-config\n" + yaml.dump(sec_base, default_flow_style=False)

if result_file is not "":
    with open(result_file, 'w') as outfile:
        outfile.write(result)
else:
    print result





