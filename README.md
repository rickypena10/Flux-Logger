# Flux-Logger
This is a simple python script used for recording serial data from select devices.

The devices are Droplet Measurement Technologies' UHSAS, Handix POPS, Campbell CSAT3b, and Gill instruments windmaster. The code can also be used to simply read serial data from an identified port. Ports are listed at the top. This code can work for Linux and Mac. I have yet to get it to work well on windows.

To run the script, first ensure that you have pyserial installed. Download the script and run:
$ python Flux_logger.py -h

this will show you the ports which have something connecte as well as the correcponding arguments. To run the code:
$ python Flux_logger.py --port '/dev/ttyU0' --instrument pops --directory ./pops_data/
or 
$ python Flux_logger.py --port '/dev/ttyU1' --instrument uhsas --directory ./uhsas_data/

When running the script for the UHSAS, the port will open immediately instead of waiting for the countdown. At this moment, you need to press run on the UHSAS gui to send the first byte or two to the linux computer. These first two bytes are the header for the file. Please note that you only need to press run the one time and leave the instrument running. After the first two bytes are read, the port will close and the countdown will begin.

I suggest running the help line multiple times to see what instrument corresponds to what port. 

Once the code is started, you should see a countdown begin. the code is set to start collecting data on the hour or half-hour mark for eddy covariance measurements. Additionally, the resulting csv's created represent a 30 minutes slot of data. 

This code can be run multiple times on a single computer for different devices. If you desire to do that, I suggest creating a screen (in linux) and then detaching and starting the next instrument(+code) before the countdown ends.
example:
$ screen -S uhsas_logging # make a screen/socket
press ctrl+a, d to exit the screen.

To reenter a screen:
$ screen -ls # list the screens available
$ screen -r uhsas_logging

finally, to kill the screen press ctrl+a, k while you are in the screen.

The ultimate goal of this code is to be a versatile tool for reading and logging data from particle counters and sonic anemometers for eddy flux studies.
