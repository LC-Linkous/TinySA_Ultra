#! /usr/bin/python3

##------------------------------------------------------------------------------------------------\
#   tinySA_python.py
#   './tinySA_python.py'
#   UNOFFICIAL Python API based on the Tiny SA Ultra official documentation at https://www.tinysa.org/wiki/
#   
#
#   Author(s): Lauren Linkous
#   Last update: January 6, 2025
##--------------------------------------------------------------------------------------------------\

import serial
import numpy as np

class TinySA():
    def __init__(self, parent=None):
        # serial port
        self.ser = None 


######################################################################
# Serial management and message processing
######################################################################

    def connect(self, port, timeout=1):
        try:
            self.ser = serial.Serial(port=port, timeout=timeout)
            return True
        except Exception as err:
            print("ERROR: cannot open port at " + str(port))
            print(err)
            return False

    def disconnect(self):
        self.ser.close()

    def tinySASerial(self, writebyte, printBool=False):
        # write out to serial, get message back, clean up, return
        
        self.ser.write(bytes(writebyte, 'utf-8'))
        msgbytes = self.getSerialReturn()
        msgbytes = self.cleanReturn(msgbytes)

        if printBool == True:
            print(msgbytes)

        return msgbytes

    def getSerialReturn(self):
        # while there's a buffer, read in the returned message
        # original buffer reading from: https://groups.io/g/tinysa/topic/tinysa_screen_capture_using/82218670

        buffer = bytes()
        while True:
            if self.ser.in_waiting > 0:
                buffer += self.ser.read(self.ser.in_waiting)
                try:
                    # split the stream to take a chunk at a time
                    # get up to '>' of the prompt
                    complete = buffer[:buffer.index(b'>')+1]  
                    # leave the rest in buffer
                    buffer = buffer[buffer.index(b'ch>')+1:]  
                except ValueError:
                    # this is an acceptable err, so can skip it and keep looping
                    continue 
                except Exception as err:
                    # otherwise, something else is wrong
                    print("ERROR: exception thrown while reading serial")
                    print(err)
                    return None
                break
        return bytearray(complete)

    def cleanReturn(self, data):
        # takes in a bytearray and removes 1) the text up to the first '\r\n' (includes the command), an 2) the ending 'ch>'
        # Find the first occurrence of \r\n (carriage return + newline)
        first_newline_index = data.find(b'\r\n')
        if first_newline_index != -1:
            # Slice the bytearray to remove everything before and including the first '\r\n'
            data = data[first_newline_index + 2:]  # Skip past '\r\n'
        # Check if the message ends with 'ch>'
        if data.endswith(b'ch>'):
            # Remove 'ch>' from the end
            data = data[:-4]  # Remove the last 4 bytes ('ch>')
        return data


######################################################################
# Serial command config, input error checking
######################################################################

    def actual_freq(self):
        # ?? It's not the max freq on the screen or center
        # usage: actual_freq
        # example return: bytearray(b'3000000000\r')
        writebyte = 'actual_freq\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False)
        return msgbytes

    def agc(self, val='auto'):
        # TODO: get documentation def of this function
        # usage: agc 0..7|auto
        # example return: bytearray(b'')

        #explicitly allowed vals
        accepted_vals =  np.arange(0, 8, 1) # max exclusive
        #check input
        if (val == "auto") or (val in accepted_vals):
            writebyte = 'agc '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)     
        else:
            print("ERROR: agc() takes vals [0 - 7]|auto")
            msgbytes =  bytearray(b'ERROR')
        return msgbytes

    def attenuate(self, val='auto'):
        # sets the internal attenuation to automatic or a specific value
        # usage: attenuate [auto|0-31]
        # example return: bytearray(b'')

        #explicitly allowed vals
        accepted_vals =  np.arange(0, 31, 1) # max exclusive
        #check input
        if (val == "auto") or (val in accepted_vals):
            writebyte = 'attenuate '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)           
        else:
            print("ERROR: attenuate() takes vals [0 - 31]|auto")
            msgbytes =  bytearray(b'')
        return msgbytes

    def bulk(self):
        # sent by tinySA when in auto refresh  mode
        # format: "bulk\r\n{X}{Y}{Width}{Height}
        # {Pixeldata}\r\n"
        # where all numbers are binary coded 2
        # bytes little endian. The Pixeldata is
        # encoded as 2 bytes per pixel
        print("Function does not exist yet. error checking needed")
        return None
    
    def calc(self):
        # sets or cancels one of the measurement modes
        # the commands are the same as those listed 
        # in the MEASURE menu
        # usage: calc off|minh|maxh|maxd|aver4|aver16|quasip
        # example return:

        #explicitly allowed vals
        accepted_vals =  ["off", "minh", "maxh", "maxd", 
                          "aver4", "aver16", "quasip"]

        print("Function does not exist yet. error checking needed")
        return None

    def caloutput(self, val):
        # disables or sets the caloutput to a specified frequency in MHz
        # usage: caloutput off|30|15|10|4|3|2|1
        # example return: bytearray(b'')

        #explicitly allowed vals
        accepted_vals =  ["off", 1,2,3,4,10,15,30]
        #check input
        if (val in accepted_vals):
            writebyte = 'caloutput '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)           
        else:
            print("ERROR: caloutput() takes vals 1|2|3|4|10|15|30|off")
            msgbytes = bytearray(b'')
        return msgbytes
    
    def capture(self):
        # requests a screen dump to be sent in binary format 
        # of 320x240 pixels of each 2 bytes
        # usage: capture
        # example return: bytearray(b'\x00 ...\x00\x00\x00')

        writebyte = 'capture\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False)    
        return msgbytes

    def clearconfig(self):
        # resets the configuration data to factory defaults. requires password
        # NOTE: does take other commands to fully clear all
        # usage: clearconfig 1234
        # example return: bytearray(b'Config and all cal data cleared.
        # \r\nDo reset manually to take effect. 
        # Then do touch cal and save.\r')

        writebyte = 'clearconfig 1234\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        return msgbytes

    def color(self):
        # sets or dumps the colors used
        # usage: color [{id} {rgb24}]
        # example return:  

        print("Function does not exist yet. error checking needed")
        return None

    def correction(self):
        # sets or dumps the frequency level orrection table
        # usage: correction [0..9 {frequency} {level}]
        # usage: correction low|lna|ultra|ultra_lna|direct|direct_lna|harm|harm_lna|out|out_direct|out_adf|out_ultra|off|on 0-19 frequency(Hz) value(dB)
        # example return:  

        print("Function does not exist yet. error checking needed")
        return None

    def dac(self, val=None):
        # sets or dumps the dac value
        # usage: dac [0..4095]
        # example return: bytearray(b'usage: dac {value(0-4095)}\r\ncurrent value: 1922\r')  

        if val == None:
            #get the dac       
            writebyte = 'dac\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)   
        elif (isinstance(val, int)) and (0<= val <=4095):
            writebyte = 'dac '+str(id)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)   
            print("dac set to " + str(id))
        else:
            print("ERROR: dac() takes either None or integers")
            msgbytes = bytearray(b'')
        return msgbytes

    def data(self, val=0):
        # dumps the trace data. 
        # usage: data [0-2]
        # 0=temp value, 1=stored trace, 2=measurement
        # example return: bytearray(b'-8.671875e+01\r\n... -8.337500e+01\r\n-8.237500e+01\r')
        
        #explicitly allowed vals
        accepted_vals = [0,1,2]
        #check input
        if val in accepted_vals:
            writebyte = 'data '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)   
        else:
            print("ERROR: data() takes vals [0-2]")
            msgbytes =  bytearray(b'')
        return msgbytes

    def deviceid(self, id=None):
        # sets or dumps a user settable number that can be use to identify a specific tinySA
        # usage: deviceid [{number}]
        # example return: bytearray(b'deviceid 12\r')

        if id == None:
            #get the device ID        
            writebyte = 'deviceid\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)   
        elif isinstance(id, int):
            writebyte = 'deviceid '+str(id)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)   
            print("device ID set to " + str(id))
        else:
            print("ERROR: deviceid() takes either None or integers")
            msgbytes =  bytearray(b'')
        return msgbytes

    def direct(self):
        # ??
        # usage: direct {start|stop|on|off} {freq(Hz)}
        # example return: ''

        print("Function does not exist yet. error checking needed")
        return None

    def ext_gain(self, val):
        # sets the external attenuation/amplification.
        # Works in both input and output mode
        # usage: ext_gain -100..100
        # example return: ''        
        
        #check input
        if (isinstance(val, int)) and (-100<= val <=100):
            writebyte = 'ext_gain '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)       
        else:
            print("ERROR: ext_gain() takes vals [-100 - 100]")
            msgbytes = bytearray(b'')
        return msgbytes

    def fill(self):
        # sent by tinySA when in auto refresh mode
        # format: "fill\r\n{X}{Y}{Width}{Height}
        # {Color}\r\n"
        # where all numbers are binary coded 2
        # bytes little endian.

        print("Function does not exist yet. error checking needed")
        return None

    def freq(self, val):
        # pauses the sweep and sets the measurement frequency.
        # tinySA: ADD LIMITS HERE
        # tinySA Ultra: 100 kHz - 5.3 GHz
        # usage: freq {frequency}
        # example return: bytearray(b'')

        #assumes val is in Hz. TODO: standardize
        #check input
        if (isinstance(val, int)) and (100*10**3<= val <=53*10**8):
            writebyte = 'freq '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)       
        else:
            print("ERROR: freq() takes integer vals [100 kHz - 5.3 GHz] as Hz for the tinySA Ultra")
            msgbytes = bytearray(b'')
        return msgbytes

        return
    
    def freq_corr(self):
        # get frequency correction
        # usage: freq_corr
        # example return: bytearray(b'0 ppb\r')

        writebyte = 'freq_corr\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        return msgbytes

    def frequencies(self):
        # dumps the frequencies used by the last
        # usage: frequencies
        # example return: bytearray(b'1500000000\r\n... \r\n3000000000\r')

        writebyte = 'frequencies\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        return msgbytes

    def help(self):
        # dumps a list of the available commands
        # usage: help
        # example return: bytearray(b'commands: freq time dac 
        # nf saveconfig clearconfig zero sweep pause resume wait
        #  repeat status caloutput save recall trace trigger
        #  marker line usart_cfg vbat_offset color if if1 lna2 
        # agc actual_freq freq_corr attenuate level sweeptime
        #  leveloffset levelchange modulation rbw mode spur 
        # lna direct ultra load ext_gain output deviceid 
        # correction calc menu text remark\r\nOther commands:
        #  version reset data frequencies scan hop scanraw test 
        # touchcal touchtest usart capture refresh touch release
        #  vbat help info selftest sd_list sd_read sd_delete 
        # threads\r')

        writebyte = 'help\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        return msgbytes

    def hop(self):
        # TODO: get documentation def of what the function is and the limits   
        # usage: hop {start(Hz)} {stop(Hz)} {step(Hz) | points} [outmask]
        # example return: ''

        print("Function does not exist yet. error checking needed")
        return None
    
    def setIF(self, val=0):
        # the IF call, but avoiding reserved keywords
        # sets the IF to automatic or a specific value. 0 means automatic
        # usage: if ( 0 | 433M..435M )
        # example return: ''

        #check input
        if (val == 0) or ((433*10**6) <=val <=(435*10**6)):
            writebyte = 'if '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)           
        else:
            print("ERROR: if() takes vals [0 |433M...435M] in Hz as integers")
            msgbytes = bytearray(b'')
        return msgbytes

    def if1(self, val):
        # TODO: get official documentation blurb
        # usage: if1 {975M..979M}\r\n977.555902MHz
        # example return: ''

        #check input
        if (val == 0) or ((975*10**6) <=val <=(979*10**6)):
            writebyte = 'if1 '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)           
        else:
            print("ERROR: if1() takes vals [0 |975M...979M] in Hz as integers")
            msgbytes = bytearray(b'')
        return msgbytes

    def info(self):
        # displays various SW and HW information
        # usage: info
        # example return: 
        # bytearray(b'tinySA ULTRA\r\n2019-2024 Copyright 
        # @Erik Kaashoek\r\n2016-2020 Copyright @edy555\r\nSW 
        # licensed under GPL. See: https://github.com/erikkaashoek
        # /tinySA\r\nVersion: tinySA4_v1.4-143-g864bb27\r\nBuild 
        # Time: Jan 10 2024 - 11:14:08\r\nKernel: 4.0.0\r\nCompiler:
        #  GCC 7.2.1 20170904 (release) [ARM/embedded-7-branch 
        # revision 255204]\r\nArchitecture: ARMv7E-M Core Variant:
        #  Cortex-M4F\r\nPort Info: Advanced kernel mode\r\nPlatform:
        #  STM32F303xC Analog & DSP\r')

        writebyte = 'info\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        return msgbytes 
    
    def level(self, val):
        # sets the output level. Not all values in the range are available
        # usage: level -76..13
        # example return: ''
        #explicitly allowed vals
        
        print("Function does not exist yet. error checking needed")
        # accepted_vals = [-76, 13]
        # #check input
        # if val in accepted_vals:
        #     writebyte = 'level '+str(val)+'\r\n'
        #     msgbytes = self.tinySASerial(writebyte, printBool=False)   
        # else:
        #     print("ERROR: level() takes vals [-76 - 13]")
        #     msgbytes =  bytearray(b'')
        # return msgbytes

        return None

    def levelchange(self, val):
        # sets the output level delta for low output mode level sweep
        # usage: levelchange -70..+70
        # example return: ''

        #explicitly allowed vals
        accepted_vals =  np.arange(-70, 71, 1) # max exclusive
        #check input
        if (val in accepted_vals):
            writebyte = 'levelchange '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)           
        else:
            print("ERROR: levelchange() takes vals [-70 - 70]")
            msgbytes =  bytearray(b'')
        return msgbytes

    def leveloffset(self):
        # sets or dumps the level calibration data.
        # For the output corrections first ensure correct output 
        # levels at maximum output level. 
        # For the low output set the output to -50dBm and
        # measure and correct the level with 
        # "leveloffset switch error" where for all output 
        # leveloffset commands measure the level with the
        # leveloffset to zero and calculate
        # error = measured level - specified level

        # usage: leveloffset low|high|switch [output] {error}

        print("Function does not exist yet. error checking needed")
        return None

    def line(self):
        # TODO: get documentation blurb for error checking
        # usage: line off|{level}\
        # example return: ''
        
        print("Function does not exist yet. error checking needed")
        return None

    def load(self, val=0):
        # loads a previously stored preset,where 0 is the startup preset 
        # usage: load [0-4]
        # example return: ''

        #explicitly allowed vals
        accepted_vals =  [0,1,2,3,4]
        #check input
        if (val in accepted_vals):
            writebyte = 'load '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)           
        else:
            print("ERROR: load() takes vals [0 - 4]")
            msgbytes = bytearray(b'')
        return msgbytes

    def lna(self, val):
        # toggle lna usage off/on
        # usage: lna off|on
        # example return: ''

        #explicitly allowed vals
        accepted_vals =  ["on", "off"]
        #check input
        if (val in accepted_vals):
            writebyte = 'lna '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)           
        else:
            print("ERROR: lna() takes vals [on|off]")
            msgbytes = bytearray(b'')
        return msgbytes

    def lna2(self, val="auto"):
        # TODO: get documentation details for any error checking
        # usage: lna2 0..7|auto
        # example return: ''

        #explicitly allowed vals
        accepted_vals =  [0,1,2,3,4,5,6,7]
        #check input
        if (val == "auto") or (val in accepted_vals):
            writebyte = 'lna2 '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)           
        else:
            print("ERROR: lna2() takes vals [0 - 7]|auto")
            msgbytes = bytearray(b'')
        return msgbytes

    def marker(self):
        # sets or dumps marker info.
        # where id=1..4 index=0..num_points-1
        # Marker levels will use the selected unit.
        # Marker peak will:
        # 1) activate the marker (if not done already), 
        # 2) position the marker on the strongest signal, and
        # 3) display the marker info.
        # The frequency must be within the selected sweep range

        # usage: marker {id} on|off|peak|{freq}|{index}
        # example return: ''

        print("Function does not exist yet. error checking needed")
        return None
    
    def mode(self):
        # sets the mode of the tinySA
        # usage: mode low|high input|output
        # example return: ''

        #TODO: check documentation to see if there's any min/max vals 
        # with those settings

        print("Function does not exist yet. error checking needed")
        return None

    def modulation(self):
        # sets the modulation in output mode
        # usage: modulation off|AM_1kHz|AM_10Hz|NFM|WFM|extern
        # example return: ''

        print("Function does not exist yet. error checking needed")
        return None

    def nf(self):
        # TODO: get documentation blurb to see if any error checking
        # usage: nf {value}\r\n5.000000000
        # example return: ''

        writebyte = 'nf\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        return msgbytes

    def output(self, val):
        # sets the output on or off
        # usage: output on|off
        # example return: ''

        # explicitly allowed vals
        accepted_vals =  ["on", "off"]
        #check input
        if (val in accepted_vals):
            writebyte = 'output '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)           
        else:
            print("ERROR: output() takes vals [on|off]")
            msgbytes = bytearray(b'')
        return msgbytes

    def pause(self):
        # pauses the sweeping in either input or output mode
        # usage: pause
        # example return: ''

        writebyte = 'pause\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        return msgbytes 

    def rbw(self, val="auto"):
        # sets the rbw to either automatic or a specific value.
        # the number specifies the target rbw in kHz
        # usage: rbw auto|3..600 
        # example return: ''

        #check input
        if (val == "auto"):
            writebyte = 'rbw '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)                
        elif (isinstance(val, int)) and (3*10**3<= val <=600*10**3):
            writebyte = 'rbw '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)           
        else:
            print("ERROR: rbw() takes vals [auto |0 - 600] in kHz as integers")
            msgbytes = bytearray(b'')
        return msgbytes

    def recall(self, val=0):
        # loads a previously stored preset,where 0 is the startup preset 
        # usage: recall [0-4]
        # example return: ''

        #explicitly allowed vals
        accepted_vals =  [0,1,2,3,4]
        #check input
        if (val in accepted_vals):
            writebyte = 'recall '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)           
        else:
            print("ERROR: recall() takes vals [0 - 4]")
            msgbytes = bytearray(b'')
        return msgbytes

    def refresh(self, val):
        # enables/disables the auto refresh mode
        # usage: refresh on|off
        # example return: ''

        #explicitly allowed vals
        accepted_vals =  ["on", "off"]
        #check input
        if (val in accepted_vals):
            writebyte = 'refresh '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)           
        else:
            print("ERROR: refresh() takes vals [on|off]")
            msgbytes = bytearray(b'')
        return msgbytes

    def release(self):
        # signals a removal of the touch
        # usage: release
        # example return: bytearray(b'')

        writebyte = 'release\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        return msgbytes 

    def repeat(self):
        # TODO: get info on exactly what this is, does, and the format
        # usage: repeat
        # example return: bytearray(b'')

        writebyte = 'repeat\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        return msgbytes 

    def reset(self):
        # reset the tinySA Ultra. NOTE: will disconnect and fully reset
        # usage: reset
        # example return: throws error. raise SerialException

        writebyte = 'reset\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        return None 

    def resume(self):
        # resumes the sweeping in either input or output mode
        # usage: resume
        # example return: ''

        writebyte = 'resume\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        return msgbytes 

    def save(self, val=1):
        # saves the current setting to a preset, where 0 is the startup preset
        # usage: save [0-4]
        # example return: ''

        #explicitly allowed vals
        accepted_vals =  [0,1,2,3,4]
        #check input
        if (val in accepted_vals):
            writebyte = 'save '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)           
        else:
            print("ERROR: save() takes vals [0 - 4] as integers")
            msgbytes = bytearray(b'')
        return msgbytes

    def saveconfig(self):
        # saves the device configuration data
        # usage: saveconfig
        # example return: bytearray(b'Config saved.\r')

        writebyte = 'saveconfig\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        return msgbytes

    def scan(self):
        # TODO: documentation for err checking
        # Performs a scan and optionally outputs the measured data.
        # usage: scan {start(Hz)} {stop(Hz)} [points] [outmask]
            # where the outmask is a binary OR of:
            # 1=frequencies, 2=measured data,
            # 4=stored data and points is maximum is 290
        print("Function does not exist yet. error checking needed")
        return None

    def scanraw(self):
        # TODO: documentation for err checking
        # performs a scan of unlimited amount of points 
        # and send the data in binary form
        # usage: scanraw {start(Hz)} {stop(Hz)} [points]
            # The measured data is send as:
            #  '{' ('x' MSB LSB)*points '}' 
            # where the 16 bit data is scaled by 32.

        print("Function does not exist yet. error checking needed")
        return None
    
    def sd_delete(self):
        # delete a specific file on the sd card
        # usage: sd_delete {filename}
        # example return:

        print("Function does not exist yet. error checking needed")
        return None
    
    def sd_list(self):
        # displays list of filenames with extension and sizes
        # usage: sd_list
        # example return: bytearray(b'-0.bmp 307322\r')

        self.ser.write(b'sd_list\r\n')
        msgbytes = self.getSerialReturn()
        msgbytes = self.cleanReturn(msgbytes)
        return msgbytes
    
    def sd_read(self):
        # read a specific file on the sd_card
        # usage: sd_read {filename}
        # example return: 

        print("Function does not exist yet. error checking needed")
        return None

    def selftest(self, val = 0):
        # performs one or all selftests
        # usage: selftest 0 0..9
        # TODO: tinySA Ultra shows 1-14 tests, not 9
        # 0 appears to be 'run all'
        # example return: msgbytes = bytearray(b'')

        # explicitly allowed vals
        accepted_vals =  [0,1,2,3,4,5,6,7,8,9]
        #check input
        if (val in accepted_vals):
            print("SELFTEST RUNNING. CONNECT CAL to RF")
            writebyte = 'selftest '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)           
        else:
            print("ERROR: selftest() takes vals [0-9]")
            msgbytes = bytearray(b'')
        return msgbytes
    
    def spur(self, val):
        # enables or disables spur reduction
        # usage: spur on|off
        # example return:

        # explicitly allowed vals
        accepted_vals =  ["on", "off"]
        #check input
        if (val in accepted_vals):
            writebyte = 'spur '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)           
        else:
            print("ERROR: spur() takes vals [on|off]")
            msgbytes = bytearray(b'')
        return msgbytes
    
    def status(self):
        # displays the current device status (paused/resumed)
        # usage: status
        # example return: bytearray(b'Resumed\r')

        writebyte = 'status\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        return msgbytes
    
    def sweep(self):
        # TODO: get info on the format and err checking
        # Set sweep boundaries or execute a sweep.
        # Sweep without arguments lists the current sweep 
        # settings. The frequencies specified should be 
        # within the permissible range. The sweep commands 
        # apply both to input and output modes        
        # usage: 
        # sweep [(start|stop|center|span|cw {frequency}) | 
        #   ({start(Hz)} {stop(Hz)} [0..290])]

        print("Function does not exist yet. error checking needed")
        return None

    def sweeptime(self):
        # sets the sweeptime
        # usage: sweep {time(Seconds)}the time
        # specified may end in a letter where
        # m=mili and u=micro
        print("Function does not exist yet. error checking needed")
        return None

    def threads(self):
        # lists information of the threads in the tinySA
        # usage: threads
        # example return:
        # bytearray(b'stklimit|        |stk free|    
        # addr|refs|prio|    state|        
        # name\r\n20000200|2000054C|00000218|200016A8|  
        #  0| 128|  CURRENT|       
        #  main\r\n20001530|2000157C|0000008C|20001650|  
        #  0|   1|    READY|        idle\r\n200053D8|200056E4
        # |000001D8|200059B0|   0| 127|    READY|       sweep\r')

        writebyte = 'threads\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        return msgbytes

    def touch(self):
        # TODO: get limits of screen
        # sends the coordinates of a touch. 
        # The upper left corner of the screen is 0 0
        # usage: touch {X coordinate} {Y coordinate}
        # example return:

        print("Function does not exist yet. error checking needed")
        return None

    def touchcal(self):
        # starts the touch calibration
        # usage: touchcal
        # example return: bytearray(b'')

        writebyte = 'touchcal\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        return msgbytes

    def touchtest(self):
        # starts the touch test
        # usage: touchtest
        # example return: bytearray(b'')

        writebyte = 'touchtest\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        return msgbytes

    def trace(self):
        # TODO: get documentation for err checking
        # displays all or one trace information
        # or sets trace related information
        # usage: 
        # trace [ {0..2} | 
        # dBm|dBmV|dBuV|V|W |store|clear|subtract | (scale|
        # reflevel) auto|{level}
        # example return: 
        print("Function does not exist yet. error checking needed")
        return None

    def trigger(self):
        # sets the trigger type or level
        # usage: trigger auto|normal|single| 
        # {level(dBm)}
        # the trigger level is always set in dBm
        # example return:  

        print("Function does not exist yet. error checking needed")
        return None

    def ultra(self):
        # turn on/config tiny SA ultra mode
        # usage: ultra off|on|auto|start|harm {freq}
        # example return: bytearray(b'')

        print("Function does not exist yet. error checking needed")
        return None

    def usart_cfg(self):
        # gets the current serial config
        # usage: usart_cfg
        # example return: bytearray(b'Serial: 115200 baud\r')

        writebyte = 'usart_cfg\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        return msgbytes

    def vbat(self):
        # displays the battery voltage
        # usage: vbat
        # example return: bytearray(b'4132 mV\r')

        writebyte = 'vbat\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        return msgbytes

    def vbat_offset(self, val=None):
        # displays or sets the battery offset value
        # usage: vbat_offset [{0..4095}]
        # example return: bytearray(b'300\r')

        if val == None:
            #get the offset       
            writebyte = 'vbat_offset\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)   
        elif (isinstance(val, int)) and (0<= val <=4095):
            writebyte = 'vbat_offset '+str(id)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)   
            print("vbat_offset set to " + str(id))
        else:
            print("ERROR: vbat_offset() takes either None or [0 - 4095] integers")
            msgbytes = bytearray(b'')
        return msgbytes

    def version(self):
        # displays the version text
        # usage: version
        # example return: tinySA4_v1.4-143-g864bb27\r\nHW Version:V0.4.5.1.1

        writebyte = 'version\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        return msgbytes

    def wait(self):
        # displays the version text
        # usage: wait
        # example return: bytearray(b'')

        writebyte = 'wait\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        return msgbytes #returns '', but does display screen

    def zero(self):
        # TODO: get info on exactly what this is, does, and the format
        # usage: zero {level}\r\n174dBm
        # example return:

        print("Function does not exist yet. error checking needed")
        return None


######################################################################
# Advanced processing, functions
######################################################################



######################################################################
# Unit testing
######################################################################

if __name__ == "__main__":
    #individual function unit test
    tsa = TinySA()
    success = tsa.connect(port='COM10') #ports depend on the OS
    if success == True:
        msg = tsa.version()
        print(msg)
        tsa.disconnect()
    else:
        print("ERR")


