"""
Custom utility exceptions 
"""

class BitMapOneError(Exception):
    """
    Declared if bitmap one length is wrong (i.e not 8 bytes).
    """

class BitMapTwoError(Exception):
    """
    Declared if bitmap two length is wrong (i.e not 8 bytes).
    """
