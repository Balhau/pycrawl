# PyCrawl

## Instalation

You need first to do a git clone from the repo

  git clone https://github.com/Balhau/pycrawl.git
  cd pycrawl

After is recommended that you install virtualenv and run your python in a sandbox to avoid dependency hell for that install virtualenv

    yum install virtualenv  #for centos based
    apt-get install virtualenv #for debian based


Inside the directory create the sandbox

    virtualenv venv #the sandbox will be put inside venv folder
    source venv/bin/activate #this will activate the sandbox

Next you need to install some external dependencies with **pip**

    pip install kazoo #for zookeeper dependencies
    pip install kafka-python #for kafka dependencies
    pip install pyyaml  #for yaml file property reading


## Running 

### Port scanner

After this steps you should be able to run the application by typing in the command line

    python pycrawl/main.py #from your main source directory

You've got also scripts to automate the spawn of process and their killing, namely

    crawler
    kcrawler

The **crawler** command spawns threads and the **kcrawler** kills them. The first command need to be parametrized like this


    ./crawler <number_of_process> <interval_between_process_spawn>

### Whois scanner

The whois scanner use the *port scanner* topic and for those ip which had open ports it will make a whois call to fetch more information regarding the host.

### Statistics tool

There is a file called *statistics.py* that will render relevant statistical information that will be collected from the topics



A more detailed talk about this project can be read [here](http://codecorner.balhau.net/a-distributed-crawler/)
