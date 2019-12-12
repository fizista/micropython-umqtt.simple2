import sys
from pathlib import Path

__dir__ = Path(__file__).absolute().parent
# Remove current dir from sys.path, otherwise setuptools will peek up our
# module instead of system's.
sys.path.pop(0)
from setuptools import setup

sys.path.append("..")
import sdist_upip


def read(file_relative):
    file = __dir__ / file_relative
    with open(str(file)) as f:
        return f.read()


setup(
    name='micropython-umqtt.simple2',
    version='2.0.0',
    description='Lightweight MQTT client for MicroPython.',
    long_description=read('README.rst'),
    long_description_content_type="text/x-rst",
    url='https://github.com/fizista/micropython-umqtt.simple2',
    author='Wojciech Banaś',
    author_email='fizista@gmail.com',
    maintainer='Wojciech Banaś',
    maintainer_email='fizista+umqtt.simple2@gmail.com',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: Implementation :: MicroPython',
    ],
    keywords='mqtt micropython',
    cmdclass={'sdist': sdist_upip.sdist},
    packages=['umqtt'],
    project_urls={
        'Bug Reports': 'https://github.com/fizista/micropython-umqtt.simple2/issues',
        'Source': 'https://github.com/fizista/micropython-umqtt.simple2',
    },
)
