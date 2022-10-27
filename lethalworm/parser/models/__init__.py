from dataclasses import dataclass

@dataclass
class LogSegment():
    """Class for parsing PseudoLogMessages.
    
    This class stores log segment.

    Args:
        time (str): segment arrival timestamp(ISO 8601)
        timestamp (float): time represented as unix timestamp float
        sessionId (str): segment Id
        message (str): message contained in segment
    """
    
    time:str
    timestamp: float
    sessionId:str
    message:str
