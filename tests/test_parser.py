import re
import pytest
import time
import dataclasses
from parser.models import LogSegment
from utils import read_file,ISO_8601_REGEX
from lethalworm import Parser


DEFAULT_LOG_LINE = "2021-05-01T00:00:13.309684 0E9D8BAD6F58CF42 status=sent"
DEFAULT_LOG_FILE = read_file('tests/mock_data_default.txt')
PERFORMANCE_LOG_FILE = read_file('tests/mock_data_performance.txt')
BROKEN_LOG_FILE = read_file('tests/mock_data_broken.txt')
DUPLICATE_LOG_FILE = read_file('tests/mock_data_duplicates.txt')

class TestInput:

    def validate_log_segment(self,log_segment:LogSegment) -> bool:
        if log_segment.message is None or len(log_segment.message) == 0: return False
        if len(log_segment.sessionId) != 16: return False
        if not isinstance(log_segment.timestamp,float): return False
        if not re.search(ISO_8601_REGEX,log_segment.time): return False

        return True

    @pytest.mark.parametrize("message_to_parse, expected_type, expected_lenght",[("",list,0),(None,list,0)])
    def test_input_empty(self,message_to_parse,expected_type,expected_lenght):
        """Parsing empty input should return empty list"""
        
        parser = Parser()

        result = parser.parse(log_messages=message_to_parse)

        assert isinstance(result,expected_type) and len(result) == expected_lenght

    @pytest.mark.parametrize("message_to_parse",[(DEFAULT_LOG_LINE)])
    def test_input_default_single(self,message_to_parse):
        """Parsing single line in correct format should return list with single LogSegment object"""

        parser = Parser()

        result_list = parser.parse(log_messages=message_to_parse)

        assert isinstance(result_list, list) and len(result_list) == 1

        result = result_list[0]
        
        assert dataclasses.is_dataclass(result)
        assert result.message == "status=sent"
        assert result.sessionId == "0E9D8BAD6F58CF42"
        assert result.time == "2021-05-01T00:00:13.309684"

    @pytest.mark.parametrize("message_to_parse",[(DEFAULT_LOG_FILE)])
    def test_input_default(self,message_to_parse):
        """Parsing default file in correct format should return list with multiple LogSegment objects"""

        parser = Parser()

        result = parser.parse(log_messages=message_to_parse)

        assert isinstance(result,list) and len(result) > 0
        
        for log_segment in result:
            assert self.validate_log_segment(log_segment=log_segment)
    
    @pytest.mark.parametrize("message_to_parse",[(PERFORMANCE_LOG_FILE)])
    def test_input_performance(self,message_to_parse):
        """Parsing 50149 lines file in correct format should return list with multiple LogSegment objects in reasonable time"""
        
        parser = Parser()

        start = time.time()
        result = parser.parse(log_messages=message_to_parse)
        end = time.time()
        assert end-start < 2, "Parser failed to parse 50149 lines per 2s"

        assert isinstance(result,list) and len(result) > 0
        
        for log_segment in result:
            assert self.validate_log_segment(log_segment=log_segment)

    @pytest.mark.parametrize("message_to_parse",[(BROKEN_LOG_FILE)])
    def test_input_broken(self,message_to_parse):
        """Parsing lines in incorrect format should not be included in result"""


        #We check here only if parser can disinguish bad formating.
        #Message Field validity will be checked at Builders 
        parser = Parser()

        result = parser.parse(log_messages=message_to_parse)

        assert isinstance(result,list) and len(result)> 0

        for log_segment in result:
            assert self.validate_log_segment(log_segment=log_segment)
    
    @pytest.mark.parametrize("message_to_parse",[(DUPLICATE_LOG_FILE)])
    def test_input_duplicates(self,message_to_parse):
        """Parsing file in correct format, but full of duplicates should return a normal list"""

        parser = Parser()

        result = parser.parse(log_messages=message_to_parse)

        assert isinstance(result,list) and len(result) > 0

        for log_segment in result:
            assert self.validate_log_segment(log_segment=log_segment)
