#!/bin/sh

JFDIR="../.."

TARGET="template_jobflow_ci_config_conA.yaml"
TMPL="template_jobflow_ci_config_appA.yaml"
VALUES="values_jobflow_conA.yaml"
python $JFDIR/render_jobflow_templates.py --template $TMPL --values $VALUES > $TARGET
echo "Input template: $TMPL"
echo "Input values  : $VALUES"
echo "Output stored : $TARGET"

TARGET="template_jobflow_ci_config_conB.yaml"
TMPL="template_jobflow_ci_config_appB.yaml"
VALUES="values_jobflow_conB.yaml"
python $JFDIR/render_jobflow_templates.py --template $TMPL --values $VALUES > $TARGET
echo "Input template: $TMPL"
echo "Input values  : $VALUES"
echo "Output stored : $TARGET"
