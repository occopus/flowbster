#!/bin/sh

SCRIPTDIR=".."
TARGET="template_jobflow_ci_config_base.yaml"
BASESYSTMPL="template_jobflow_ci_config_frame_sys.yaml"
BASEAPPTMPL="template_jobflow_ci_config_frame_app.yaml"
python $SCRIPTDIR/create_jobflow_template_frames.py --base $BASESYSTMPL --scriptdir $SCRIPTDIR > $TARGET
cat $BASEAPPTMPL >> $TARGET
echo "Input sys template: $BASESYSTMPL"
echo "Input app template: $BASEAPPTMPL"
echo "Output stored in  : $TARGET"

