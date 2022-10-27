from builder.models import Email, EmailTime
from parser.models import LogSegment

from utils import ISO_8601_REGEX,timestamp_to_iso8601

import re
import logging
from datetime import datetime,timezone

log = logging.getLogger(__name__)

class Parser:
    """This is a pseudo log message parser class"""
    
    def _extract_timestamp(self,string_line:str) -> str:
        #We use regex to extract time from log_segment
        log_message_timestamp = re.findall(ISO_8601_REGEX,string_line)
        
        #Assuring that only 1 valid value is found. If more or less than 1 value is found its a strong indication of failure, so we drop it.
        assert len(log_message_timestamp) == 1, ""        
        
        return log_message_timestamp[0]
    
    def _get_timestamp(self,timestamp_iso8601:str) -> float:
        #We will be using timestamp for asses race condictions for lists of log_segments. Also, for calculating session durations.
        return datetime.strptime(timestamp_iso8601, "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone.utc).timestamp()

    def _extract_sessionId(self,string_line:str) -> str:



        #First we split by time. This provides us with clear/default structure.
        splitted_message = re.split(ISO_8601_REGEX,string_line)[1:]
            
        assert len(splitted_message) == 1, ""

        #Next we find all middle values of log_segments. This middle value is clasified as sessionId.
        #Fixing DeprecationWarning: invalid escape sequence '\s' with double \\
        log_message_session_id = re.findall('^(?:...)[^\\s]*',splitted_message[0])

        #A little bit of cleaning
        log_message_session_id = log_message_session_id[0].replace(" ","")

        #sessionId is of lenght 16. We need to verify it 
        assert len(log_message_session_id) == 16, ""

        return log_message_session_id

    def _extract_message(self,string_line:str) -> str:
        
        splitted_message = re.split(ISO_8601_REGEX,string_line)[1:]
        assert len(splitted_message) == 1, ""

         #Fixing DeprecationWarning: invalid escape sequence '\s' with double \\
        splitted_message = re.split("^(?:...)[^\\s]*",splitted_message[0])[1:]

        assert len(splitted_message) == 1, ""

        message = splitted_message[0].replace(" ","").replace("\n","")

        return message
    
    def _validate_log_segment(self,log_segment:LogSegment) -> bool:
        if log_segment.message is None or len(log_segment.message) == 0: return False
        if len(log_segment.sessionId) != 16: return False
        if not isinstance(log_segment.timestamp,float): return False
        if not re.search(ISO_8601_REGEX,log_segment.time): return False

        return True

    def _parse(self,string_line:str,line_index:int = 0) -> LogSegment:
        try:
            if re.search(ISO_8601_REGEX,string_line):
                
                log_message_time = self._extract_timestamp(string_line)

                log_message_timestamp = self._get_timestamp(log_message_time)

                log_message_session_id = self._extract_sessionId(string_line)

                message = self._extract_message(string_line)

                log_segment = LogSegment(time=log_message_time,timestamp=log_message_timestamp,sessionId=log_message_session_id,message=message)
                



                return log_segment

        except Exception:
            log.error("{0} Error: Failed to parse message -> {{ {1} }} at line: {2}".format(datetime.now(),string_line,line_index))
            return None

    def parse(self,log_messages:str) -> list[LogSegment]:
        
        log_buffer:list[LogSegment] = []

        if log_messages == None:
            return log_buffer


        if isinstance(log_messages,list):
            for index,line in enumerate(log_messages):
                parsed_log_line = self._parse(string_line=line,line_index=index)
                
                if parsed_log_line and self._validate_log_segment(log_segment=parsed_log_line):
                    log_buffer.append(parsed_log_line)

        elif isinstance(log_messages,str):
            parsed_log_line = self._parse(string_line=log_messages)
            if parsed_log_line:
                    log_buffer.append(parsed_log_line)

        return log_buffer

class Builder:
    """This class builds Email messages from parsed log segments."""

    def _assemble_message(self,log_segments:list[LogSegment]) -> Email:
        """Returns a single :class:`models.email.Email` instance representing
        the assembled messages.

        :param log_segments: A list of log message segments,
        :type log_segments: list[LogSegment]
        :return: A single instance of the discovered :class:`models.email.Email` objects
        :rtype: `models.email.Email`
        """


        #Email template is used as a validation template to check if all mandatory fields are set;
        email_template = {
            "status":None,
            "client":None,
            "from":None,
            "to":None,
            "message-id":None
        }
        
        #All segments are grouped by sessionid, so we can just take the first one from list and assign its sessionId;
        sessionid = log_segments[0].sessionId
        
        #All segments in the same session are sorted according to timestamp, First element == newest message;
        session_start_time = log_segments[0].time
        
        #Previously we have parsed ISO8601 Date to timestamp. Now we can compare newest message against oldest message in the list. This way we get session duration;
        session_duration = log_segments[-1].timestamp - log_segments[0].timestamp
        
        assert session_duration >= 0, ""

        #Converting duration in seconds to timedelta represented as string;
        session_duration = str(timestamp_to_iso8601(session_duration))

        #Building required Time format for Email Log Message;
        time = EmailTime(start=session_start_time,duration=session_duration)
        
        
        #Extracting fields and their values from message object; 
        for item in log_segments:

            #Regex to find a field(from,to,client,messageid,status)
            field = re.findall("^[^=]*",item.message)[0]

            #Regex to extract first value after we get a field;
            value = re.findall("[^=]*$",item.message)[0]

            #We check if this is a valid field;
            if field in email_template:
                email_template[field] = value
            else:
                log.error(f"{datetime.now()} Error: Failed to assemble email. Unrecognized field -> {field}")
        

        #We iterate through template to ensure all fields are set. If any field is missing we need to drop this message;
        for item in email_template.items():
            if item[1] == None:
                return None
        
        #Building email object
        return Email.build_from_template(message_template=email_template,sessionid=sessionid,time=time)
    
    def build_message(self,log_buffer:list[LogSegment]) -> list[Email]:
        """Returns a list of :class:`models.email.Email` objects. 

        :param log_segments: A list of log message segments,
        :type log_segments: list[LogSegment]
        :return: A list of :class:`models.email.Email` objects
        :rtype: list[`models.email.Email`]
        """
        
        #We will be storing segments as dictionary -> { sessionId:[log_segments] }
        session_map = {}
        
        #Here we will store a full list of successfuly parsed messages(emails)
        messages = []
        
        
        #First lets populate our session_map with log_segments.
        #This is achieved by grouping all log_segments stored at log_buffer by sessionIds;
        for item in log_buffer:
            if item.sessionId in session_map:
                session_map[item.sessionId].append(item)
            else:
                session_map.update({item.sessionId:[item]})
        

        #Next we itterate again to check if any sessionIds have more than 1 log_segments.
        #This will indicate that this sessionId is worth exploring;
        for key,value in session_map.items():
            if len(value) > 1:
                #We sort log_segments by timestamp values to ensure that first element in list is newest one and last one is oldest;
                sorted_by_timestamp = sorted(value, key=lambda x: x.timestamp)

                #We update session_map with sorted log_segment lists.
                session_map[key] = sorted_by_timestamp

                #We can try to assemble message(email) from sorted log_segments.
                #If all required fields were collected we get an Email object;
                #else we get None;
                message = self._assemble_message(log_segments=sorted_by_timestamp)
                if message:
                    messages.append(message)
                
        
        return messages

# if __name__ == "__main__":

#     c = Parser()
#     b = Builder()

#     with open(r"C:\Users\LukasPetravicius\Documents\Github\lethal_worm\lethalworm\mockdata.txt") as data_mock:
#         mock_data = data_mock.readlines()
    


#     # log_message = "2021-05-01T00:00:07.319452 A87246FB7082775D status=rejected"

#     log_segments = c.parse(mock_data)
#     email = b.build_message(log_segments)
#     print(email)
