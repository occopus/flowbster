#!/bin/sh

JFDIR="../.."
TARGET="template_jobflow_ci_config_con.yaml"
TMPL="template_jobflow_ci_config_app.yaml"
VALUES="values_jobflow_con.yaml"

python $JFDIR/render_jobflow_templates.py --template $TMPL --values $VALUES > $TARGET
echo "Input template: $TMPL"
echo "Input values  : $VALUES"
echo "Output stored : $TARGET"

