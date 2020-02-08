import intelhex
hexFile='b.hex'
binFile='b_from_intelhex_library.bin'

ih = intelhex.IntelHex()
ih.loadhex(hexFile) 
ih.tobinfile(binFile)