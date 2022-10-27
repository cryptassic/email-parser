import pytest
from lethalworm import Parser
from lethalworm import Builder


from pprint import pprint as pp
from utils import read_file


DEFAULT_LOG_LINE = "2021-05-01T00:00:13.309684 0E9D8BAD6F58CF42 status=sent"
DEFAULT_LOG_FILE = read_file('tests/mock_data_default.txt')
PERFORMANCE_LOG_FILE = read_file('tests/mock_data_performance.txt')
BROKEN_LOG_FILE = read_file('tests/mock_data_broken.txt')
DUPLICATE_LOG_FILE = read_file('tests/mock_data_duplicates.txt')

class TestInput:

    @pytest.mark.parametrize("message_to_parse, expected_type, expected_lenght",[("",list,0),(None,list,0)])
    def test_input_empty(self,message_to_parse:str,expected_type:type, expected_lenght:int):
        """Parsing empty input should return empty list"""

        parser = Parser()
        builder = Builder()

        
        empty_list = parser.parse(log_messages=message_to_parse)

        assert isinstance(empty_list,list) and len(empty_list) == 0

        result = builder.build_message(log_buffer=empty_list)


        assert isinstance(result,expected_type) and len(result) == expected_lenght

    @pytest.mark.parametrize("message_to_parse",[(DEFAULT_LOG_LINE)])
    def test_input_default_single(self,message_to_parse:str):
        """Parsing single line should return empty list"""

        parser = Parser()
        builder = Builder()

        log_segment = parser.parse(log_messages=message_to_parse)

        result = builder.build_message(log_buffer=log_segment)

        assert isinstance(result,list) and len(result) == 0

    @pytest.mark.parametrize("message_to_parse",[(DEFAULT_LOG_FILE)])
    def test_input_default(self,message_to_parse:str):
        """Parsing default file should return normal message"""

        parser = Parser()
        builder = Builder()

        log_segments = parser.parse(log_messages=message_to_parse)

        result = builder.build_message(log_buffer=log_segments)

        assert isinstance(result,list) and len(result) == 1

        assert result[0].address.from_ == '<charles.brown@example.com>'
        assert result[0].address.to == '<barbara.brown@example.com>'
        assert result[0].client == '10.192.162.239'
        assert result[0].messageid == '<3455937c-58c9-4dae-b057-692d4dd26684@PKCKUO0ORJ>'
        assert result[0].sessionid == '09E8698600CF8B32'
        assert result[0].status == 'rejected'
        assert result[0].time.duration == '0:00:18.553392'
        assert result[0].time.start == '2021-05-01T00:00:07.117297'

    @pytest.mark.parametrize("message_to_parse",[(BROKEN_LOG_FILE)])
    def test_input_broken(self,message_to_parse:str):
        """Parsing broken file should return no message"""

        parser = Parser()
        builder = Builder()

        log_segments = parser.parse(log_messages=message_to_parse)

        result = builder.build_message(log_buffer=log_segments)

        assert isinstance(result,list) and len(result) == 0
