# PIOmxControl

This is a web interface for RaspberryPI and omxplayer. This enable a device with a web browser
to search for movies, to play and stop. This is a very elementary tool but it is the bare minimum to
control the movies with your smartphone

Next steps:

* Fix design
* Add controllers

##Software needed

This front end application use on back end some utility programs you need to install first to successfully run this program. They are needed, for example, to render video on raspberry, parse and download media stream from public endpoints and to play and stop stream of audio (for example for the radio mechanism).
Without further add here are the programs:

* omxplayer: Program to render video
* youtube-dl: Program to parse media endpoints and retrieve video stream
* mpd: Daemon to reproduce audio
* mpc: Utility to parse and reproduce endpoints

## To install

To install you can follow the instructions presented in the [docker project](http://git.balhau.net/docker.git/) more specifically under [this module](http://git.balhau.net/docker.git/tree/master/omxclient/). To install the dependencies you can just reproduce the steps done in the [Dockerfile](http://git.balhau.net/docker.git/blob/master/omxclient/Dockerfile). Notice, however, that the instructions are for centos distributions, so you need to make some adjustments if you got a Debian based distribution.

If you just want to run the application without much fuss you can just follow the instructions presented there and run the component in Docker containers by following the instructions presented there.

For those who want to install manually in a host environment you can just install the package from the [pip repository](http://pip.balhau.net/simple) by running

    pip install omxclient --upgrade --extra-index-url  http://pip.balhau.net/simple

## To run

To run the app you need to find your distribution packages folder and then run the *main.py* file. In the debian based distributions you can do it like this

    sudo nohup python /usr/local/lib/python2.7/dist-packages/omxclient/main.py &

The nohup and is needed if you want to run the process in background. The logs will go to nohup.out file

## Next development steps

The next feature I want to provide is the ability to list the pending download operations. Currently we hold the list of pending downloading requests on a rabbitmq queue. This will be replaced by a combination of a in memory queue with the help of a SQLite database for persistence reasons. This will add a litle more of complexity but will add, hopefully, a little more of resilience  than the current solution. The problem is that the requests take a fair amount of time to process and this causes timeout errors in the current rabbitmq consumer. Additionally the use of rabbitmq is an external dependency that adds complexity to the utility. This can be tackled in a simpler way by this new strategy.
