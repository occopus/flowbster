import argparse
from jinja2 import Template
import yaml

file_template="template.yaml"
file_values="values.yaml"
file_out=""

def load_template(path):
    with open(path, 'r') as f:
        return f.read()

def load_values(path):
    with open(path, 'r') as f:
        return yaml.load(f)

parser = argparse.ArgumentParser(description='Performs rendering template using values.')
parser.add_argument('--template', help='specifies the template to be rendered')
parser.add_argument('--values', help='specifies values to use for rendering')
parser.add_argument('--outfile', help='specifies the output file where the result is written.')
args = parser.parse_args()

if args.template is not None:
    file_template=args.template
if args.values is not None:
    file_values=args.values
if args.outfile is not None:
    file_out=args.outfile

tmpl_str = load_template(file_template)
template = Template(tmpl_str)
values = load_values(file_values)
result = template.render(values)

if file_out is not "":
    with open(file_out, 'w') as outfile:
        outfile.write(result)
else:
    print result


