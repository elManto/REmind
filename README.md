# REmind

Final repository for the study about Reverse Engineering behaviors

## Data collection

### Python virtual env

We have several dependencies (angr to generate the assembly, flask for the web-ui, mysql, ...). The first step is to build a proper python3 virtualenv:

1. mkvirtualenv -p python3 re\_webui
2. pip install -r requirements.tx 

All the following steps assume you set up the virtual environment and installed the requirements

### How to generate disassembly and other binary analysis files

Simply, from the root directory of the repo, run:

        ./deploy_chall.sh /path/to/binary_file /path/to/output


### Deploy a new challenge

As of now, you just need to edit the config.ini accordingly to the new chall configurations, then adding a blueprint using the template_chall.py as a skeleton, and of course read the previous point for the disassembly/strings/binary info generation. 

For the frontend, the `static` directory includes the three main .js files that work as a library to make the challenge running. Just include them in an .html file with the name of the chall and copy the .html skeleton if you don't want any specific behavior.

TODO: implement an automatic way of doing that...

### How to run the whole system

From the root directory of the repo:

1. export FLASK_APP=re-webui
2. export FLASK_ENV=development
3. flask run --host=0.0.0.0


## Results evaluation

Give a look to the README in the `results_analysis/` directory 
