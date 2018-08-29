import O22SIOUT
import sys
import struct
import socket

class O22MMP:
    def __init__(self, host=None):
        if(host is None): host = '127.0.0.1'
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host,2001))
        self.tlabel = 0 # Transaction label is unused.


## MISC MMP ACCESS FUNCTIONS
##
# ReadRawOffset
    def ReadRawOffset(self, offset, size, data_type):
        data = self.ReadBlock(int(offset, 16), size)
        return self.UnpackReadResponse(data, data_type)
# LastError
    def LastError(self):
        data = self.ReadBlock(O22SIOUT.BASE_LAST_ERROR, 4)
        return str(hex(int(self.UnpackReadResponse(data, 'i')))).upper()[2:]
# UnitDescription
    def UnitDescription(self):
        data = self.ReadBlock(O22SIOUT.BASE_UNIT_DESCRIPTION, 12)
        return self.UnpackReadResponse(data, 'NONE')
# FirmwareVersion
    def FirmwareVersion(self):
        data = self.ReadBlock(O22SIOUT.BASE_FIRMWARE_VERSION, 4)
        return self.UnpackReadResponse(data, 'FIRMWARE')

## ETHENET STATUS ACCESS FUNCTIONS
##
# Eth0 STATUS
    def IPAddressE0(self):
        data = self.ReadBlock(O22SIOUT.BASE_IP_ADDRESS_ETH0, 4)
        return self.UnpackReadResponse(data, 'IP')
    def MACAddressE0(self):
        data = self.ReadBlock(O22SIOUT.BASE_MAC_ADDRESS_ETH0, 6)
        return self.UnpackReadResponse(data, 'MAC')
# Eth1 STATUS
    def IPAddressE1(self):
        data = self.ReadBlock(O22SIOUT.BASE_IP_ADDRESS_ETH1, 4)
        return self.UnpackReadResponse(data, 'IP')
    def MACAddressE1(self):
        data = self.ReadBlock(O22SIOUT.BASE_MAC_ADDRESS_ETH1, 6)
        return self.UnpackReadResponse(data, 'MAC')



## HD DIGITAL POINTS
##
    def GetDigitalPointState(self, module, channel):
        offset = (O22SIOUT.BASE_DPOINT_READ
                + (module * O22SIOUT.OFFSET_DPOINT_MOD)
                + (channel * O22SIOUT.OFFSET_DPOINT))
        data = self.ReadBlock(offset, 4)
        return int(self.UnpackReadResponse(data, 'i'))

## SetDigitalPointState
    def SetDigitalPointState(self, module, channel, state):
        offset = (O22SIOUT.BASE_DPOINT_WRITE
                + (module * O22SIOUT.OFFSET_DPOINT_MOD)
                + (channel * O22SIOUT.OFFSET_DPOINT))
        data = self.WriteBlock(offset, [0,0,0,state])
        return self.UnpackWriteResponse(data)


## ANALOG POINTS
##
## GetAnalogPointValue
    def GetAnalogPointValue(self, module, channel):
        offset = (O22SIOUT.BASE_APOINT_READ
                + (O22SIOUT.OFFSET_APOINT_MOD * module)
                + (O22SIOUT.OFFSET_APOINT * channel))
        data = self.ReadBlock(offset, 4)
        return float(self.UnpackReadResponse(data, 'f'))

## SetAnalogPointValue
    def SetAnalogPointValue(self, module, channel, value):
        offset = (O22SIOUT.BASE_APOINT_WRITE
                + (O22SIOUT.OFFSET_APOINT_MOD * module)
                + (O22SIOUT.OFFSET_APOINT * channel))
        data = self.WriteBlock(offset, self.PackFloat(value))
        return self.UnpackWriteResponse(data)

## MIN / MAX VALUES
## GetAnalogPointMin
    def GetAnalogPointMin(self, module, channel):
        offset = (O22SIOUT.BASE_APOINT_READ
                + (O22SIOUT.OFFSET_APOINT_MOD * module)
                + (O22SIOUT.OFFSET_APOINT * channel)
                + O22SIOUT.OFFSET_APOINT_MIN)
        data = self.ReadBlock(offset, 4)
        return float(self.UnpackReadResponse(data, 'f'))

## GetAnalogPointMax
    def GetAnalogPointMax(self, module, channel):
        offset = (O22SIOUT.BASE_APOINT_READ
                + (O22SIOUT.OFFSET_APOINT_MOD * module)
                + (O22SIOUT.OFFSET_APOINT * channel)
                + O22SIOUT.OFFSET_APOINT_MAX)
        data = self.ReadBlock(offset, 4)
        return float(self.UnpackReadResponse(data, 'f'))


## SCRATCHPAD ACCESS FUNCTIONS
##
## INTEGERS
# GetScratchPadIntegerArea
    def GetScratchPadIntegerArea(self, index):
        if (index < 0 or index > O22SIOUT.MAX_ELEMENTS_INTEGER):
            return 'index out of bounds'
        offset = O22SIOUT.BASE_SCRATCHPAD_INTEGER + (index * 0x04)
        data = self.ReadBlock(offset, 4)
        return int(self.UnpackReadResponse(data, 'i'))

# SetScratchPadIntegerArea
    def SetScratchPadIntegerArea(self, index, value):
        if (index < 0 or index > O22SIOUT.MAX_ELEMENTS_INTEGER):
            return 'index out of bounds'
        offset = O22SIOUT.BASE_SCRATCHPAD_INTEGER + (index * 0x04)
        data = self.WriteBlock(offset, self.PackInteger(value))
        return self.UnpackWriteResponse(data)

## FLOATS
# GetScratchPadFloatArea
    def GetScratchPadFloatArea(self, index):
        if (index > O22SIOUT.MAX_ELEMENTS_FLOAT):
            return 'index out of bounds'
        offset = O22SIOUT.BASE_SCRATCHPAD_FLOAT + (index * 0x04)
        data = self.ReadBlock(offset, 4)
        return float(self.UnpackReadResponse(data, 'f'))

# SetScratchPadFloatArea
    def SetScratchPadFloatArea(self, index, value):
        if (index > O22SIOUT.MAX_ELEMENTS_FLOAT):
            return 'index out of bounds'
        offset = O22SIOUT.BASE_SCRATCHPAD_FLOAT + (index * 0x04)
        data = self.WriteBlock(offset, self.PackFloat(value))
        return self.UnpackWriteResponse(data)

## STRINGS
# GetScratchPadStringArea
    def GetScratchPadStringArea(self, index):
        loc = index * O22SIOUT.OFFSET_SCRATCHPAD_STRING
        if (loc >= O22SIOUT.MAX_BYTES_STRING) or (index < 0):
            return 'index out of bounds'
        offset = O22SIOUT.BASE_SCRATCHPAD_STRING + loc
        sizeData = self.ReadBlock(offset+0x01, 1)
        rawSize = self.UnpackReadResponse(sizeData, 'c')[1:-1]
        # rawSize is char `c` *or* a hex `/x00` number. Convert to int:
        size = ord(rawSize) if len(rawSize)==1 else int('0'+rawSize[1:], 16)
        # Note: string size is at offset + 1, string data is at offset + 2
        data = self.ReadBlock(offset+0x02, size)
        return self.UnpackReadResponse(data, 'NONE')

# SetScratchPadStringArea
    def SetScratchPadStringArea(self, index, value):
        if (len(value) > 127): return 'string must be < 128 characters'
        loc = index * O22SIOUT.OFFSET_SCRATCHPAD_STRING
        if(loc >= O22SIOUT.MAX_BYTES_STRING):
            return 'index out of bounds'
        offset = O22SIOUT.BASE_SCRATCHPAD_STRING + loc + 0x02 
        hexvals = []
        for i in range(len(value)):
            hexvals.append(ord(value[i]))
        data = self.WriteBlock(offset, hexvals)
        return self.UnpackWriteResponse(data)


## UNPACK BLOCK RESPONSE DATA
##
## UnpackReadResponse
    def UnpackReadResponse(self, data, data_type):
        data_block = data[16:]
        output = ''
        # Unpack data and build firmware version string "NV.vc".
        #       Version comes in [V, v, N, c] HEX format.
        if data_type == 'FIRMWARE':
            version = []
            for i in range(4):
                raw = struct.unpack_from('>c', bytearray(data_block[i]))
                nextChar = str(raw)[4:-3]
                version.append(nextChar)
            # Replace `N` with A, B, R, S or ?
            if   int(version[2]) == 0:  output = 'A'
            elif int(version[2]) == 1:  output = 'B'
            elif int(version[2]) == 2:  output = 'R'
            elif int(version[2]) == 3:  output = 'S'
            else:                       output = '?'
            # Replace `c` with 0 = 'a', 1 = 'b', ... using chr(..+97)
            output += (str(int(version[0])) + '.'
                    + str(int(version[1])) + chr(int(version[3])+97))
        # Unpack data and format as an IP address.
        elif data_type == 'IP':
            for i in range(len(data_block)):
                raw = struct.unpack_from('>c', bytearray(data_block[i]))
                # Trim first 3 and last 3 around <data>: ('/<data>',)
                nextChar = str(raw)[3:-3]
                # Catch:  10  =(hex)=>  0x0A  =(ascii)=>  \n  =(trim)=>  'n'
                if(nextChar == 'n'): nextChar = 10
                else: nextChar = int('0'+nextChar, 16) # hex -> decimal
                output += str(nextChar) + '.'
            output = output[:-1] # Trim trailing '.'
        # Unpack data and format as a MAC address.
        elif data_type == 'MAC':
            for i in range(len(data_block)):
                # Trim first 2 last 3 around <data>: ('<data>',)
                raw = struct.unpack_from('>c', bytearray(data_block[i]))
                nextChar = str(raw)[2:-3]
                # Force valid ascii (single-character) back into hex.
                if(len(nextChar) == 1): nextChar = hex(ord(nextChar))
                output += nextChar[2:] + '-' # Trim 0x, add dash.
            output = output[:-1].upper() # Trim trailing '-'
        # Unpack data that has no formatting.
        elif data_type == 'NONE':
            output = data_block
        # Unpack data of a specific given struct data_type (c, i, f, etc.)
        #   *Convert type after calling the function.*
        else:
            raw = struct.unpack_from('>'+data_type, bytearray(data_block))
            output = str(raw)[1:-2]
        return output

## UnpackWriteResponse
    def UnpackWriteResponse(self, data):
        data_block = data[4:8]
        status = struct.unpack_from('>i', bytearray(data_block))
        return int(str(status)[1:-2])


## METHODS TO PACKAGE DATA INTO HEX ARRAYS
##
## PackFloat
    def PackFloat(self, value):
        valueToWrite = hex(struct.unpack('L', struct.pack('f', value))[0])
        hexvals = []
        if(value != 0):
            for i in range(4):
                hexvals.append(int(str(valueToWrite)[(2*i)+2:(2*i)+4], 16))
        else: hexvals = [0, 0, 0, 0]
        return hexvals
## PackInteger
    def PackInteger(self, value):
        hexvals = [0, 0, 0, value]
        if(value > 255):
            hexvals = [0, 0, 0, 0]
            value = hex(value)
            evenLength = (len(str(value)) % 2 == 0)
            # Force all values to have even length for byte-wise splitting:
            value = str(value)[2:] if(evenLength) else ('0'+str(value)[2:])
            for i in range(len(value)/2): # Split value into max. 0xFF bytes.
                thisPart = int(str(value)[(2*i):(2*i)+2], 16)
                hexvals[i+(4-len(value)/2)] = thisPart
        return hexvals


## CORE MEMORY ACCESS FUNCTIONS
##
## ReadBlock
    def ReadBlock(self, address, size):
        block = self.BuildReadBlockRequest(address, size)
        nSent = self.sock.send(block)
        return self.sock.recv(O22SIOUT.SIZE_READ_BLOCK_RESPONSE + size)

## WriteBlock
    def WriteBlock(self, address, value):
        block = self.BuildWriteBlockRequest(address, value)
        nSent = self.sock.send(block)
        return self.sock.recv(O22SIOUT.SIZE_WRITE_RESPONSE)

## BLOCK REQUEST BYTE ARRAY CONSTRUCTORS
##
## BuildReadBlockRequest
    def BuildReadBlockRequest(self, dest, size):
        tcode = O22SIOUT.TCODE_READ_BLOCK_REQUEST
        block = [
            0, 0, (self.tlabel << 2), (tcode << 4), 0, 0, 255, 255,
            int(str(hex(dest))[2:4],16), int(str(hex(dest))[4:6],16),
            int(str(hex(dest))[6:8],16), int(str(hex(dest))[8:10],16),
            0,size, 0,0
            ]
        return bytearray(block)

## BuildWriteBlockRequest
    def BuildWriteBlockRequest(self, dest, data):
        tcode = O22SIOUT.TCODE_WRITE_BLOCK_REQUEST
        block = [
            0, 0, (self.tlabel << 2), (tcode << 4), 0, 0, 255, 255,
            int(str(hex(dest))[2:4],16), int(str(hex(dest))[4:6],16),
            int(str(hex(dest))[6:8],16), int(str(hex(dest))[8:10],16),
            0,len(data), 0,0
            ]
        return bytearray(block+data)

## CLOSE SOCKET / END SESSION
    def close(self):
        self.sock.close()
