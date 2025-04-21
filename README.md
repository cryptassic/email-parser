# DEMO Email Parser
## _Custom Log parser for log analysis system_

[![N|Python3](https://www.python.org/static/community_logos/python-powered-w-70x28.png)](https://www.python.org/)

Email Parser is a custom build for one of cybesecurity analysit job interview. It is a efficient, pseudo email log parser.

## Features

- Combines events bassed on the session id
- Incomplete sessions are droped automatically
- Events can be handled in parallel
- Additionally calculates session duration
- Prints out a formated log in JSON

## Installation

Lethal Worm requires [Python 3](https://www.python.org/downloads/) to run.


System level:
```sh
git clone https://github.com/cryptassic/lethal_worm.git 
cd lethal_worm
python3 setup.py install
```

User level:
```sh
python3 setup.py install --user
```

## Usage
```sh
demo.py [-h] file [file ...]
```

## Examples

Simple parse file by running the code
```python
from lethalworm import App

if __name__ == "__main__":
    app = App()
    app.run(log_filename="tests/mock_data_default.txt")
```




Or simply parse single lines and build your own Builder!
```python
from lethalworm import Parser,read_file

if __name__ == "__main__":
    parser = Parser()
    example_log_line = "2021-05-01T00:00:07.117297 09E8698600CF8B32 client=10.192.162.239"
    
    parsed_log_line = parser.parse(log_messages=example_log_line)
    
    assert parsed_log_line.message == "client=10.192.162.239"
    assert parsed_log_line.sessionid == "client=09E8698600CF8B32"
    assert parsed_log_line.time == "2021-05-01T00:00:07.117297"
```


## Development

Want to contribute? Great!

Lethal Worm uses simple Python 3 language for fast developing, so it's really easy to jump in and start building.

## License

MIT

**Free Software, Hell Yeah!**
**This README is built using Dillinger**

