"""
Module contains the DataElementFormat class and DATA_ELEMENT_FORMAT dictionary
"""
from dataclasses import dataclass

@dataclass
class DataElementFormat:
    """
    Describes the data element format
    """
    content_type: str
    is_fixed: bool
    field_max_length: int
    meaning: str

DATA_ELEMENT_FORMAT = {
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
