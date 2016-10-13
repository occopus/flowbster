import yaml
import os
import argparse

content_script="contentS:"
content_template="contentT:"
script_dir=""
template_dir=""
base_template_name="template_jobflow_ci_config_frame_sys.yaml"
result_file=""

def load_base_template(path):
    with open(path, 'r') as f:
        return yaml.load(f)

def load_file(fullpath):
    with open(fullpath, 'r') as f:
        return f.read()

def replace_contents_of_files(sec_base):
    for files_to_read in sec_base['write_files']:
        if content_script == files_to_read["content"][0:len(content_script)]:
            filename = files_to_read["content"][len(content_script):]
            content_file=load_file(os.path.join(script_dir,filename))
            files_to_read["content"]=content_file
        elif content_template == files_to_read["content"][0:len(content_template)]:
            filename = files_to_read["content"][len(content_template):]
            content_file=load_file(os.path.join(template_dir,filename))
            files_to_read["content"]=content_file
    return sec_base

parser = argparse.ArgumentParser(description='Create jobflow sys base template containing the jobflow scripts.')
parser.add_argument('--base', help='specifies the base sys template without scripts')
parser.add_argument('--scriptdir', help='specifies the directory containing the jobflow scripts')
parser.add_argument('--tmpldir', help='specifies the directory containing the jobflow templates')
parser.add_argument('--outfile', help='specifies the file where the template is written')
args = parser.parse_args()

if args.base is not None:
    base_template_name=args.base
if args.scriptdir is not None:
    script_dir=args.scriptdir
if args.tmpldir is not None:
    template_dir=args.tmpldir
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





