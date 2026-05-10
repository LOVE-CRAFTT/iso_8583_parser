"""
ISO 8583 Parser
"""
from data_element_format import DATA_ELEMENT_FORMAT

MTI_BYTE_SIZE = 4
BITMAP_BYTE_SIZE = 8

secondary_bitmap_available = False

SAMPLE_HEX_STRING ="""
            30 32 30 30 F2 38 44 80 20 C0 80 00 00 00 00 00
            00 00 00 00 31 36 34 31 31 31 31 31 31 31 31 31
            31 31 31 31 31 31 30 30 30 30 30 30 30 30 30 30
            30 30 30 35 30 30 30 30 30 34 31 35 31 34 33 30
            32 32 31 32 33 34 35 36 31 34 33 30 32 32 30 34
            31 35 35 34 31 31 30 32 31 30 30 33 37 34 31 31
            31 31 31 31 31 31 31 31 31 31 31 31 31 31 3D 32
            35 31 32 31 30 31 31 32 33 34 35 30 30 30 30 30
            30 30 54 45 52 4D 30 30 30 31 4D 45 52 43 48
            41 4E 54 31 32 33 20 20 20 20 35 36 36"""
raw_bytes = bytes.fromhex(SAMPLE_HEX_STRING)

# mti is the first four bytes
mti_bytes = raw_bytes[:MTI_BYTE_SIZE]
mti = [chr(digit) for digit in mti_bytes]


# read the next 8 bytes, determine presence of secondary bitmap and data elements from binary fields
# set flag accordingly
# possibly read next 8 bytes to determine next data elements
# return a list of the set bits for testing
bmp_1_bytes = raw_bytes[MTI_BYTE_SIZE: MTI_BYTE_SIZE + BITMAP_BYTE_SIZE]
bmp_bin_string = ''.join([format(byte, "08b") for byte in bmp_1_bytes])

# Indicates position of cursor/pointer in the bytes object
# used later for keeping position when reading data elements
raw_byte_position =  MTI_BYTE_SIZE + BITMAP_BYTE_SIZE

secondary_bitmap_available = bmp_bin_string[0] == "1"

if secondary_bitmap_available:
    bmp_2_bytes = raw_bytes[MTI_BYTE_SIZE + BITMAP_BYTE_SIZE : MTI_BYTE_SIZE +
                            (BITMAP_BYTE_SIZE * 2)]
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
        available_data_elements.append(index + 1)
    index += 1


# main loop
for element_index in available_data_elements:

    # TODO: confirm type based on content_type
    field_max_length = DATA_ELEMENT_FORMAT[element_index].field_max_length

    #for fixed length data elements
    if DATA_ELEMENT_FORMAT[element_index].is_fixed:
        data_bytes = raw_bytes[raw_byte_position: raw_byte_position + field_max_length]
        DATA_STRING = ''.join([chr(byte) for byte in data_bytes])
        raw_byte_position += field_max_length
        print(element_index, DATA_STRING, DATA_ELEMENT_FORMAT[element_index].meaning)

    else:
        # The length of the field_max_length is the number of bytes to read
        # to get actual number of bytes for that data element
        length_of_field_max_length = len(str(field_max_length))
        data_element_length_bytes = raw_bytes[raw_byte_position :
                                              raw_byte_position + length_of_field_max_length]
        raw_byte_position += length_of_field_max_length

        actual_data_element_byte_length = int(''.join([chr(byte) for byte
                                                       in  data_element_length_bytes]))
        data_bytes = raw_bytes[raw_byte_position: raw_byte_position +
                               actual_data_element_byte_length]
        DATA_STRING = ''.join([chr(byte) for byte in data_bytes])
        raw_byte_position += actual_data_element_byte_length
        print(element_index, DATA_STRING, DATA_ELEMENT_FORMAT[element_index].meaning)
