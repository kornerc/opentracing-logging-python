import versioneer
from setuptools import find_packages, setup

setup(
    name='logging_opentracing',
    packages=find_packages(exclude=['tests', 'tests/*']),
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='OpenTracing handler for the Python logging library',
    author='Clemens Korner',
    license='MIT',
    url='https://github.com/kornerc/python-logging-opentracing',
    install_requires='opentracing'
)
