from setuptools import find_packages, setup

setup(
    name="lethalworm",
    version="1.0",
    author="Lukas Petravicius",
    description="Log parser",
    url="https://github.com/cryptassic/lethal_worm",
    python_requires = '>=3.7, <4',
    packages=find_packages(include=['lethalworm'])
)