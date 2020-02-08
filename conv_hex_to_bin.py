# Refer to the following url
#     https://en.wikipedia.org/wiki/Intel_HEX

offsetAddress = 0
binBuffer     = []
data          = {}

RECORD_TYPE_DATA                     = 0
RECORD_TYPE_END_OF_FILE              = 1
RECORD_TYPE_EXTENDED_SEGMENT_ADDRESS = 2
RECORD_TYPE_EXTENDED_LINEAR_ADDRESS  = 4

def parsingHex(recordType, address, dat):
    global offsetAddress
    global binBuffer
    global data
    
    if(recordType == RECORD_TYPE_DATA):
        data[offsetAddress+address] = dat
        #print(hex(offsetAddress+address))

    elif(recordType == RECORD_TYPE_END_OF_FILE): #end of file
        #print('end of file')
        res = sorted(data.items())
        lists = list(res)
        curAddress = lists[0][0]

        for v in lists:
            #print('{0} {1} {2}'.format(hex(curAddress), len(v[1]), hex(v[0])))
            if(curAddress != v[0]):                
                print(' - pad start {0}, size {1}'.format(hex(curAddress), hex(v[0]-curAddress)))
                padBuf = [0xFF for j in range(v[0]-curAddress)]
                binBuffer.append(padBuf)    

            binBuffer.append(v[1])    
            curAddress = (v[0] + len(v[1]))

    elif(recordType == RECORD_TYPE_EXTENDED_SEGMENT_ADDRESS): #extend address
        offsetAddress = ((dat[0]<<8)|dat[1])<<4  #or ((dat[0]<<8)|dat[1])*16
        #print('extend segment address {0}'.format(hex(offsetAddress)))

    elif(recordType == RECORD_TYPE_EXTENDED_LINEAR_ADDRESS): #extend address
        offsetAddress = ((dat[0]<<8)|dat[1])<<16 #or ((dat[0]<<8)|dat[1])*65536
        #print('extend linear address {0}'.format(hex(offsetAddress)))


def decodeLine(line):
    line = line.rstrip()

    comma      = readComma(line)
    byteLen    = readByteLen(line)
    address    = readAddress(line)
    recordType = readRecordType(line)
    dat        = readData(line)
    checksum   = readChecksum(line)

    calCheck   = calculateChecksum(line)
    
    if(calCheck == checksum):
        #print('it is correct data')
        #print('byte len:{0}, address: {1}, type: {2}, checksum: {3}'.format(byteLen, address, recordType, checksum))
        parsingHex(recordType, address, dat)
    else:
        print('it is wrong data [{0} {1}]'.format(calCheck, checksum))


def asciiHexToInt(ascii):
    dat = ord(ascii.upper())
    if(dat >= 0x41):
        dat = (dat-0x41)+10
    else:
        dat = dat-0x30
    return dat

def stringToInt(dat):
    val = 0
    for c in dat:
        val <<= 4
        val |= asciiHexToInt(c)
    return val 

def readComma(line):
    return line[0]

def readByteLen(line):
    return stringToInt(line[1:3])

def readAddress(line):
    return stringToInt(line[3:7])

def readRecordType(line):
    return stringToInt(line[7:9])

def readData(line):
    buf = []
    dat = line[9:-2] # data start position = 9
    for i in range(0, len(dat), 2):
        buf.append(stringToInt(dat[i:i+2]))
        #print('%x' % stringToInt(dat[i:i+2]), end='')
    #print('')    
    return buf

def readChecksum(line):
    return stringToInt(line[-2:])

def calculateChecksum(line):
    dat = line[1:-2] # checksum range
    check = 0
    for i in range(0, len(dat), 2):        
        check += stringToInt(dat[i:i+2])
    
    # two's complement
    check = ((0xFF-(check & 0xFF))+1) & 0xFF 
    return check

if __name__ == "__main__":  
    hexFile = 'b.hex'
    binFile = 'b.bin'

    with open(hexFile, "r") as f:
        lines = f.readlines()
        for line in lines :
            decodeLine(line)
        
        with open(binFile, 'wb') as wf:
            for b in binBuffer:
                wf.write(bytes(b))
            print('Conversion completed.')