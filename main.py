"""
ISO 8583 Parser
"""

MTI_BYTE_SIZE = 4
BITMAP_BYTE_SIZE = 8

secondary_bitmap_available = False

HEX_STRING ="""30 32 30 30 F2 38 44 80 20 C0 80 00 00 00 00 00 00 00 00 00
            31 36 34 31 31 31 31 31 31 31 31 31
            31 31 31 31 30 30 30 30 30 30 30 30 30 30 30 30
            30 35 30 30 30 30 30 34 31 35 31 34 33 30 32 32
            31 32 33 34 35 36 31 34 33 30 32 32 30 34 31 35
            35 34 31 31 30 32 31 30 30 33 37 34 31 31 31 31
            31 31 31 31 31 31 31 31 31 31 31 3D 32 35 31 32
            31 30 31 31 32 33 34 35 30 30 30 30 30 30 30 30
            30 54 45 52 4D 30 30 30 31 4D 45 52 43 48 41 4E
            54 31 32 33 20 20 20 20 35 36 36"""
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

# Indicates position of cursor/pointer in the bytes object
# used later for keeping position when reading data elements
raw_byte_position =  MTI_BYTE_SIZE + BITMAP_BYTE_SIZE

secondary_bitmap_available = bmp_bin_string[0] == "1"

if secondary_bitmap_available:
    bmp_2_bytes = raw_bytes[MTI_BYTE_SIZE + BITMAP_BYTE_SIZE : MTI_BYTE_SIZE + (BITMAP_BYTE_SIZE * 2)]
    BMP_2_BIN_STRING = ''.join([format(byte, "08b") for byte in bmp_2_bytes])
    bmp_bin_string += (BMP_2_BIN_STRING)

    # position is now at the end of second bitmap
    raw_byte_position = MTI_BYTE_SIZE + (BITMAP_BYTE_SIZE * 2)


# get indexes of available data elements
# remove indexes 0 and 64, corresponding to data elements 1 and 65
# they represent existence of bitmaps and are not useful data themselves
# removing them prevents if statements checking for their existence later
available_data_elements = []
index = 0
while index < len(bmp_bin_string):
    if bmp_bin_string[index] == '1' and index not in (0, 64):
        available_data_elements.append(index)
    index += 1


#TODO: Look into dataclass
class DataElementFormat:
    """
    Describes the data element format
    """
    def __init__(self, content_type: str, is_fixed: bool, field_max_length: int, meaning: str):
        self.content_type = content_type
        self.is_fixed = is_fixed
        self.field_max_length = field_max_length
        self.meaning = meaning

data_element_format = {
    1 : DataElementFormat('b', True, 16, 'Bitmap'),
    2 : DataElementFormat('n', False, 19, "Primary account number (PAN)"),
    3 : DataElementFormat('n', True, 6, 'Processing Code'),
    4 : DataElementFormat('n', True, 12, 'Amount Transaction'),
    7 : DataElementFormat('n', True, 10, 'Transmission date & time'),

    11 : DataElementFormat('n', True, 6, 'System trace audit number (STAN)'),
    12 : DataElementFormat('n', True, 6, 'Local transaction time(hhmmss)'),
    13 : DataElementFormat('n', True, 4, 'Local transaction date(MMDD)'),
    18 : DataElementFormat('n', True, 4, 'Merchant type/category code'),
    22 : DataElementFormat('n', True, 3, 'Point of service entry mode'),
    25 : DataElementFormat('n', True, 2, 'Point of service condition code'),
    35 : DataElementFormat('z', False, 37, 'Track 2 data'),
    41 : DataElementFormat('ans', True, 8, 'Card acceptor terminal identification'),
    42 : DataElementFormat('ans', True, 15, 'Card acceptor identification code'),
    49 : DataElementFormat('a or n', True, 3, 'Currency code, transaction'),
}
