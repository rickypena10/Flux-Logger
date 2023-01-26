#!/home/farmerlab/anaconda3/envs/COMP/bin/python
"""
Created on Nov 11 16:00:00 2022, V2

@author: Ricardo L. Peña
penar@colostate.edu
Affiliation: Colorado State University

Here, the windmaster was set to  "U,V,W,SOS,Temp"  mode.
The program generates a new text file in the same folder as this program
every 30 min and writes the data.

This code was developed by sampling code from the following locations
Serial reading  -->  www.DavesMotleyProjects.com
File creation   -->  Copyright (c) <2019> <Christian Ahlers, Marc Buckley>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import io
import os
import sys
import time
import datetime
import glob
import serial
from argparse import ArgumentParser

from time import sleep      # to create delays
from locale import format   # to format numbers
#from shutil import rmtree   # to remove directories
import logging

#dir_path = "/Users/FarmerLab/Desktop/PENA/Projects/Serial_logging/Davesmotleyprojects"

def log_err_warn(error_message): #logging errors and warnings.
    logger = logging.getLogger('data_stream')
    logger.basicConfig(filename = 'error.log', level=logging.DEBUG,
        format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p') # displaying data and
    logger.warning('logging a warning')
    logger.error('logging an error:\n{}'.format(error_message))

def serial_ports():
    #check the type of system in use. I want this to be os independent.
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i+1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-a]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')
    #try connecting to ports
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    print("\n####################### Accessible ports! ########################")
    print(result)
    print("##################################################################\n")
    return result

def input_arguments(): # arguments that are user defined
    # run script + -h to list current ports and see arguments.
    parser = ArgumentParser()
    parser.add_argument('--instrument', type = str, default = 'serial',
        help = 'Select instrument in use: csat3b, windmaster, pops or uhsas')
    parser.add_argument('--port', type = str, help = 'Select the appropriate serial port in use.')
    parser.add_argument('--directory', type = str, default = os.getcwd(),
        help = 'Select the directory where you want files saved (default = current directory).')
    arguments = parser.parse_args()
    return arguments

def open_port(serial_port, baudrate, instrument_type):
    #accessing/opeing the computer serial port
    if instrument_type == "csat3b":
        ser = serial.Serial(
            port = serial_port,
            baudrate = baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            rtscts = True,
            xonxoff= True,
            dsrdtr= True,
            timeout=0)
    else:
        ser = serial.Serial(
            port = serial_port,
            baudrate = baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            rtscts = True,
            timeout=0)

    print(ser)
    print(ser.name)
    print("Serial port is open: ", ser.isOpen())
    return ser

def define_header(serial_port, baudrate, instrument_type):
    ser0 = open_port(serial_port, baudrate, instrument_type)
    header_0 = serial_read(ser0, instrument_type)
    header_1 = serial_read(ser0, instrument_type)
    header0 = header_0.split("\r")[0].split("\t")
    header1 = header_1.split("\r")[0].split('\t')
    joint_header = [i+"_"+j for i,j in zip(header0, header1)]
    header_string = ','.join(map(str, joint_header))
    ser0.close()
    print ("Serial port is open: ", ser0.isOpen())
    return header_string

def bin_headers(nbins, logmin, logmax):
    # The number of bins, logmin, and log max can change.
    # Check the POPS_BBB.cfg file to ensure the correct values are used.
    delta = (logmax - logmin)/nbins
    #print(delta)

    lower = [round(10**logmin,2)]
    upper = [round(10**(logmin+delta),2)]

    for i in range(1,nbins):
        bin_number = i+1
        l = round(10**(logmin+((bin_number-1)*delta)),2)
        u = round(10**(logmin+(bin_number*delta)),2)
        lower.append(l)
        upper.append(u)
    joint_header = [str(i)+"_"+str(j) for i,j in zip(lower, upper)]
    header_string = ','.join(map(str, joint_header))
    return header_string


def create_logging_file(dir_path, instrument_type, file_heading):
    print(dir_path)
    try:
        #create header based on anemometer type
        if instrument_type == "windmaster":
            #creating file - Adapted from Chri'/dev/ttyUSB0'stian Ahlers and Marc Buckley
            fname = 'windmaster_%y%m%d%H%M%S.csv'  # set filename with appendix:YYMMDDHHMMSS

            timing = "Index,Day_CPU(YYYY-MM-DD),time_CPU(HH:MM:SS.FFF),"
            wind_mag = "Start_codon,u(m/s),v(m/s),w(m/s),"
            extras = "unit_ident,SOS(m/s),T(Celsius),Error_code,Check_sum\n"
            header = timing+wind_mag+extras

        elif instrument_type == "csat3b":
            fname = 'csat3b_%y%m%d%H%M%S.csv'  # set filename with appendix:YYMMDDHHMMSS

            timing = "Index,Day_CPU(YYYY-MM-DD),time_CPU(HH:MM:SS.FFF),"
            wind_mag = "u_x(m/s),u_y(m/s),u_z(m/s),"
            extras = "T(Celsius),Diagnostic_code,record_counter,sig_hex\n"
            header = timing+wind_mag+extras

        elif instrument_type == "uhsas":
            fname = 'uhsas_%y%m%d%H%M%S.csv'  # set filename with appendix:YYMMDDHHMMSS

            timing = "Index,Day_CPU(YYYY-MM-DD),time_CPU(HH:MM:SS.FFF),"
            header = timing+file_heading

        elif instrument_type == "pops":
            fname = 'pops_%y%m%d%H%M%S.csv'  # set filename with appendix:YYMMDDHHMMSS

            bins = 16
            logmin = 1.759
            logmax = 4.806
            bin_header = bin_headers(bins, logmin, logmax)
            #print(bin_header)
            ID = "Name, Serial, DateTime(YYYYMMDD),Time(S Unix-epoch),"
            stats1 = "Particle_con(cc),POPS_flow(sccm),POPS_P(hPa),POPS_T(C),"
            stats2 = "Data_status, baseline(counts), stdev_baseline, max_stdev,"
            stats3 = "PumpFB(PID),LaserT(C),LaserFB(PID),Laser_Monitor,Voltage(V),"
            header = ID+stats1+stats2+stats3+bin_header+"\n"

        elif instrument_type == "serial":
            fname = 'serial_%y%m%d%H%M%S.csv'  # set filename with appendix:YYMMDDHHMMSS
            header = ""


        # create file and append header line for csat3b or windmaster
        filename = time.strftime(fname) # start time molded to fname format
        filename_path = dir_path + "/"+ filename
        fid = open(filename_path,'a+') # open first fid
        fid.write(header) # write header into file
        fid.close()
        return filename_path

    except Exception as e:
        print("no instrument selected!")

def serial_read(ser, instrument_type):
    valueString = ""        # reset the string that will collect decoded characters.
    mchar = ser.read()      # read one byte character from the serial port.
    terminal_bit = b'\n'    # default end of line termination.
    if instrument_type == "windmaster": terminal_bit = b'\r'
    # gill datastream ending indicated by b'\r' while csat and other instruments'
    # analogue outputs may be terminated by the b'\n' character.

    # make sure that the first byte read isn't a terminal character.
    if (mchar == terminal_bit):
        mchar = ser.read()

    # continue reading characters until a 'new line' or terminal character is received.
    while (mchar != terminal_bit):
        # appending translated character to the valueString
        valueString += mchar.decode(encoding = 'ascii')
        mchar = ser.read() # read the nxt byte.
    #print("ascii outside: ", str(valueString))
    return valueString

    """Value string has no characters. mchar reads the first bit.
    Based on that initial bit, a while loop kicks in. This loop continues
    to read bits, appends the decoded/translated bit to valueString, reads
    the next bit, and replaces the initial mchar value.
    When the mchar bit is equal to b'\r' indicating the termination of a line,
    the loop stops and valueString is set equal to nothing. The cycle starts over.
    """


# reading and writing serial data to file
def read_data(ser, dataIndex, filename, instrument_type):
    dataString = serial_read(ser, instrument_type)
    # after a full dataString has been assembled, create the timestamp
    millis = int(round(time.time() * 1000))
    rightNow = str(datetime.datetime.now()).split()
    mDate = rightNow[0]
    mTime = rightNow[1]

    #anemometers output comma separated data, so data doesnt need formating
    # time, date, and index columns are added
    if instrument_type == "csat3b" or instrument_type == "windmaster":
        # format the full string: index, timestamp, and data.
        fileString = "{:05d}".format(dataIndex) + ", " + str(mDate) + ", " + \
            str(mTime) + "," + dataString

    #uhsas outputs tab separated data. It needs to be converted to comma
    # separated data
    elif instrument_type == "uhsas":
        split_string = dataString.split("\r")[0].split("\t")
        fixed_dataString = ','.join(map(str, split_string))
        fileString = "{:05d}".format(dataIndex) + ", " + str(mDate) + ", " + \
            str(mTime) + "," + fixed_dataString

    # Or we can just output the raw data from the instrument
    else: fileString = dataString

    print(fileString) # displays current data/fileString to the terminal
    #append data to file:
    fid = open(filename,'a+')
    fid.write(fileString+"\n")
    fid.close()

def countdown(min, sec):
    second_count = 59 - sec

    # determine if we're closer to the hour or half hour. negative time shouldn't
    # be displayed.
    if (min < 30):
        min_count_30 = 30 - min
        timer = '\tCountdown until data collection (MM:SS):\t{:02d}:{:02d}'.format(min_count_30-1, second_count)
        print(timer, end="\r")

    elif (min > 30):
        min_count_60 = 60 - min
        timer = '\tCountdown until data collection (MM:SS):\t{:02d}:{:02d}'.format(min_count_60-1, second_count)
        print(timer, end="\r")
    sleep(1)


def main(args):
    # initial user defined parameters
    dir_path = args.directory
    print('{} is the current storage directory.'.format(dir_path))

    instrument_type = args.instrument
    addr = args.port
    baud = 9600 ## baud rate for instrument
    header = None # header can be hardcoded
    if instrument_type == 'csat3b':
        baud = 115200
    if instrument_type == 'uhsas': # header read from instrument
        baud = 115200
        # uhsas file heading is variable and is output by the instrument
        # the header must be read from the first byte or two.
        print("checking UHSAS header...")
        header = define_header(addr, baud, instrument_type)
        #print(header)

    # Key chunk of code to run everything
    try:
        while(True): # always measure time
            local_time = datetime.datetime.now()
            local_min, local_sec = local_time.minute, local_time.second

            #time trigger to move on to data recording. Start recoring data at
            # 0 min, 0 sec or on the half hour(30 min), 0 sec
            if local_sec == 0 and (local_min == 0 or local_min == 30):
            #if local_sec == 0:
                global ser
                ser = open_port(addr, baud, instrument_type) #open port at time limit
                while(True): # when triggered, always run this chunk of code
                    try:
                        #create the logging csv to write to.
                        file_name = create_logging_file(dir_path, instrument_type, header)
                        print("#################################")
                        print("New file created!")
                        print("#################################")

                        fileInterval = 1800    # sec, new file every 30 mins
                        #fileInterval = 30    # sec, see if it works
                        starttime = time.time()

                        dataIndex = 0
                        # while the time interval is less than the file interval
                        # time (30 min), read data from the anemometer
                        while((time.time() - starttime) < fileInterval):
                            read_data(ser, dataIndex, file_name, instrument_type)
                            dataIndex += 1
                    except UnicodeDecodeError as e: # may be a decoding bug here.
                        #maybe start using logger here to log errors
                        log_err_warn(e)
                        print(e)
                        continue # bypass the bug and continue collecting data.
            else: # if we havent reached the hour or half hour mark
            # dont record any data, instead just display the time remaing till the
            # nearest hour or half hour
                countdown(local_min, local_sec)
    except KeyboardInterrupt as e: # if ctrl + c pushed, stop everything
        if 'ser' in globals():
            ser.close()
            print ("Serial port is open: ", ser.isOpen())
        print("Data collection stopped!")
    return 0


if __name__ == '__main__':
    ports = serial_ports()
    args = input_arguments()
    main(args)
