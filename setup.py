from setuptools import setup, find_packages

setup(
    name="fydesktop",
    version="0.0.1",
    url="https://github.com/wanghuiwen1/fydesktop",
    author="wanghuiwen",
    author_email="wanghuiwen312@sina.com",
    license="MIT",
    description="fydesktop is a Python 3 script",
    long_description="fydesktop is a Python 3 script",
    install_requires=["threadpool","appdirs","pillow","apscheduler"],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'fydesktop = fydesktop.__main__:main',
        ]}
)
