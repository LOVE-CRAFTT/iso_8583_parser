"""
ISO 8583 Parser
"""

MTI_BYTE_SIZE = 4
BITMAP_BYTE_SIZE = 8

secondary_bitmap_available = False

HEX_STRING ="""
            30 32 30 30 F2 38 44 80 20 C0 80 00 00 00 00 00 00 00 00 00
            """
raw_bytes = bytes.fromhex(HEX_STRING)

# mti is the first four bytes
mti_bytes = raw_bytes[:MTI_BYTE_SIZE]
mti = [chr(digit) for digit in mti_bytes]


# read the next 8 bytes, determine presence of secondary bitmap and data elements from binary fields
# set flag accordingly
# possibly read next 8 bytes to determine next data elements
# run the bitwise or operation on each to determine if a bit is "set"
# return a list of the set bits for testing
bmp_1_bytes = raw_bytes[MTI_BYTE_SIZE: MTI_BYTE_SIZE + BITMAP_BYTE_SIZE]
bmp_bin_string = ''.join([format(byte, "08b") for byte in bmp_1_bytes])

secondary_bitmap_available = bmp_bin_string[0] == "1"

if secondary_bitmap_available:
    bmp_2_bytes = raw_bytes[MTI_BYTE_SIZE + BITMAP_BYTE_SIZE : MTI_BYTE_SIZE + (BITMAP_BYTE_SIZE * 2)]
    BMP_2_BIN_STRING = ''.join([format(byte, "08b") for byte in bmp_2_bytes])
    bmp_bin_string += (BMP_2_BIN_STRING)

print(len(bmp_bin_string))
