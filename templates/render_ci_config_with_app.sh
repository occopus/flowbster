#!/bin/sh

TARGET="jobflow_ci_config_with_app.yaml"
TMPL="template_jobflow_ci_config_base.yaml"
VALUES="values_jobflow_app.yaml"

echo $*

if [ $# -gt 0 ]; then
    VALUES=$1
fi
if [ $# -gt 1 ]; then
    TARGET=$2
fi

python render_jobflow_templates.py --template $TMPL --values $VALUES > $TARGET
echo "Input template: $TMPL"
echo "Input values  : $VALUES"
echo "Output stored : $TARGET"

