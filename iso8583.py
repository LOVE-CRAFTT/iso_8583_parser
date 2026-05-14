"""
ISO 8583 Parser
"""
# import pprint
import json
from data_element_format import DATA_ELEMENT_FORMAT

MTI_BYTE_SIZE = 4
BITMAP_BYTE_SIZE = 8

def get_mti(message_bytes: bytes):
    """
    Message Type Indicator (MTI)
    """
    # mti is the first four bytes
    mti_bytes = message_bytes[:MTI_BYTE_SIZE]
    mti_list = [chr(digit) for digit in mti_bytes]
    mti_string = ''.join(mti_list)
    return mti_string


def get_avail_data_elems_and_next_idx(message_bytes: bytes) -> tuple[list, int]:
    """
    This function returns a tuple containing the available data elements
    and index of next read operation.
    """
    # read the next 8 bytes,
    # determine presence of secondary bitmap and data elements from binary fields
    # set flag accordingly
    # possibly read next 8 bytes to determine next data elements
    bmp_1_bytes = message_bytes[MTI_BYTE_SIZE: MTI_BYTE_SIZE + BITMAP_BYTE_SIZE]
    bmp_bin_string = ''.join([format(byte, "08b") for byte in bmp_1_bytes])

    # Indicates position of cursor/pointer in the bytes object
    # used later for keeping position when reading data elements
    raw_byte_position =  MTI_BYTE_SIZE + BITMAP_BYTE_SIZE

    secondary_bitmap_available = bmp_bin_string[0] == "1"

    if secondary_bitmap_available:
        bmp_2_bytes = message_bytes[raw_byte_position : raw_byte_position + BITMAP_BYTE_SIZE]
        bmp_2_bin_string = ''.join([format(byte, "08b") for byte in bmp_2_bytes])
        bmp_bin_string += (bmp_2_bin_string)

        # position is now at the end of second bitmap
        raw_byte_position += BITMAP_BYTE_SIZE

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
    return (available_data_elements, raw_byte_position)


def iso_8583_to_json(iso_8583_hex_string) -> str:
    """
    Convert an iso 8583 message --given as a hexadecimal string--
    and return a JSON string
    """
    # contains parsed data
    parsed_message_dict = {}

    raw_bytes = bytes.fromhex(iso_8583_hex_string)

    mti = get_mti(raw_bytes)
    parsed_message_dict[0] = mti

    available_data_elements, raw_byte_position = get_avail_data_elems_and_next_idx(raw_bytes)

    # main loop
    for element_index in available_data_elements:
        field_max_length = DATA_ELEMENT_FORMAT[element_index].field_max_length
        content_type = DATA_ELEMENT_FORMAT[element_index].content_type
        is_fixed_length_de = DATA_ELEMENT_FORMAT[element_index].is_fixed

        #for fixed length data elements
        if is_fixed_length_de:

            # special case if content_type is x+n:
            # an extra byte is read
            # because the first byte is either C or D for credit or debit
            if content_type == 'x+n':
                field_max_length += 1

            # another special case if its a binary field DE,
            # bytes will "resolve" to hexadecimal values since its binary information
            # else its ASCII/unicode
            data_bytes = raw_bytes[raw_byte_position: raw_byte_position + field_max_length]
            if content_type == 'b':
                data_string = ''.join([format(byte, '02X') for byte in data_bytes])
            else:
                data_string = ''.join([chr(byte) for byte in data_bytes])
            raw_byte_position += field_max_length
            parsed_message_dict[element_index] = data_string

        # for variable length data elements
        else:
            # The length of the field_max_length is the number of bytes to read
            # to get actual number of bytes for that data element
            length_of_field_max_length = len(str(field_max_length))
            data_element_length_bytes = raw_bytes[raw_byte_position :
                                                raw_byte_position + length_of_field_max_length]
            raw_byte_position += length_of_field_max_length

            actual_data_element_byte_length = int(''.join([chr(byte) for byte
                                                        in  data_element_length_bytes]))
            # special case if content_type is x+n:
            # an extra byte is read
            # because the first byte is either C or D for credit or debit
            if content_type == 'x+n':
                actual_data_element_byte_length += 1

            data_bytes = raw_bytes[raw_byte_position: raw_byte_position +
                                actual_data_element_byte_length]
            data_string = ''.join([chr(byte) for byte in data_bytes])
            raw_byte_position += actual_data_element_byte_length
            parsed_message_dict[element_index] = data_string



    # completely parsed message to be used as desired
    # pprint.pp(parsed_message_dict)
    parsed_message_json = json.dumps(parsed_message_dict, indent=0)
    return parsed_message_json


if __name__ == "__main__":
    # Sample from sarvatra technologies
    SAMPLE_HEX_STRING = """
        30 32 32 30 72 3A 80 11 2C A1 C0 10 31 36 30 30
        30 30 30 30 30 30 30 30 30 30 30 39 39 38 31 39
        30 30 30 30 30 30 30 30 30 30 30 32 30 30 30 30
        31 31 32 30 30 39 31 35 32 32 38 31 38 35 33 33
        30 39 31 35 32 32 31 31 32 30 31 31 32 30 31 31
        32 30 43 30 30 30 30 30 30 30 30 30 34 31 31 31
        31 33 31 31 30 30 30 30 30 30 30 31 32 33 34 35
        36 37 38 44 32 30 30 32 31 32 36 30 30 30 32 31
        38 30 31 33 32 34 30 39 38 31 38 35 33 33 30 32
        33 37 35 38 39 30 30 34 32 30 30 31 4D 41 49 4E
        20 42 52 41 4E 43 48 20 20 20 20 20 20 20 20 20
        20 20 50 45 54 48 20 56 41 44 47 41 4F 4E 20 4D
        48 20 49 4E 30 31 36 31 30 30 30 30 30 30 30 31
        32 33 34 35 36 37 38 33 35 36 33 35 36 30 31 36
        32 30 31 31 32 30 31 31 32 30 31 31 32 30 31 31
    """

    message_json = iso_8583_to_json(SAMPLE_HEX_STRING)
    print(message_json)
