#!/bin/bash

echo "This is stdout."
echo "This is stderr." >&2

COUNTER=""
INPUT="input"
FILTER=""
OUTPUT="output"
FORMAT=""

echo "DEFAULT settings:"
echo "INPUT: $INPUT"
echo "OUTPUT: $OUTPUT"
echo "FILTER: $FILTER"
echo "FORMAT: $FORMAT"
echo "COUNTER: $COUNTER"

while [[ $# > 0 ]]
do
key="$1"

case $key in
    -f|--filter)
    FILTER="$2"
    shift # past argument
    ;;
    -m|--format)
    FORMAT="$2"
    shift # past argument
    ;;
    -c|--counter)
    COUNTER="$2"
    shift # past argument
    ;;
    -i|--input)
    INPUT="$2"
    shift # past argument
    ;;
    -o|--output)
    OUTPUT="$2"
    shift # past argument
    ;;
    *)
    ;;
esac
shift # past argument or value
done

echo "ACTUAL settings:"
echo "INPUT: $INPUT"
echo "OUTPUT: $OUTPUT"
echo "FILTER: $FILTER"
echo "FORMAT: $FORMAT"
echo "COUNTER: $COUNTER"

touch "$OUTPUT"
if [ "$FILTER" == "" ]; then
    echo "Input: single"
    echo -n "Copying... "
    cat $INPUT >> $OUTPUT
    echo "Done."
else
    echo "Input: collector"
    echo -n "Copying... "
    for i in `ls $FILTER*`;
    do
        cat $i >> "$OUTPUT"
    done
    echo "Done."
fi

if [ "$FORMAT" == "" ] || [ "$COUNTER" == "" ] || [ "$COUNTER" -lt 2 ]; then
    echo "Output: single"
    echo "Nothing to be done."
else
    echo "Output: generator"
    echo -n "Copying... "
    MAX=$(($COUNTER-1))
    for i in `seq 0 $MAX`;
    do
        FNAME="$FORMAT"$i
        echo "Generated file" > $FNAME
        echo "Index: $i" >> $FNAME
        echo "Max: $COUNTER" >> $FNAME
        echo "Inputs: " >> $FNAME
        cat $OUTPUT >> $FNAME
    done
    rm $OUTPUT
    echo "Done."
fi




