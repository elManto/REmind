#!/bin/bash

# usage: ./deploy_chall.sh path/to/binary path/to/outdir

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR

PATH_TO_BINARY=$1
OUTPUT_PATH=$2

SCRIPTS='./scripts'

if [ -z "$PATH_TO_BINARY" ] || [ -z "$OUTPUT_PATH" ]
then
	echo "Missing one or more arguments"
	echo "Usage ./deploy_chall.sh path/to/binary path/to/output/directory"
	exit
fi

mkdir -p $OUTPUT_PATH 
python $SCRIPTS/get_binary_info.py $PATH_TO_BINARY $OUTPUT_PATH
python $SCRIPTS/get_strings_second_version.py $PATH_TO_BINARY $OUTPUT_PATH # Change angr offset in case of PIE

