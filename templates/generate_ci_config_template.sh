#!/bin/sh

TARGET="template_jobflow_ci_config.yaml"
BASESYSTMPL="template_jobflow_sys_base.yaml"
BASEAPPTMPL="template_jobflow_app_base.yaml"
python create_jobflow_template_frames.py --base $BASESYSTMPL --scriptdir .. > $TARGET
cat $BASEAPPTMPL >> $TARGET
echo "Input sys template: $BASESYSTMPL"
echo "Input app template: $BASEAPPTMPL"
echo "Output stored in  : $TARGET"

