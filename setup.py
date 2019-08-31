from setuptools import setup, find_packages

setup(
    name="fwdesktop",
    version="0.0.1",
    url="http://fwdesktop.org/fwdesktop",
    author="wanghuiwen",
    author_email="wanghuiwen312@sina.com",
    license="MIT",
    description="fwdesktop is a Python 3 script",
    long_description="fwdesktop is a Python 3 script",
    install_requires=["threadpool","appdirs","pillow"],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'fwdesktop = fwdesktop.__main__:main',
        ]}
)
