"""
Custom utility exceptions 
"""

class BitMapOneError(Exception):
    """
    Raised if bitmap one length is wrong (i.e not 8 bytes).
    """

class BitMapTwoError(Exception):
    """
    Raised if bitmap two length is wrong (i.e not 8 bytes).
    """

class MTIError(Exception):
    """
    Raised if insufficient data is provided to decode the MTI.
    Or if MTI value is invalid
    """

class DataElementError(Exception):
    """
    Raised if insufficient data is provided to decode the a data element.
    """
