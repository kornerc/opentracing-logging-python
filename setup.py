import versioneer
from setuptools import find_packages, setup

setup(
    packages=find_packages(exclude=['tests', 'tests/*']),
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    install_requires=['opentracing>=2.1,<3.0'],
    tests_require=['pytest'],
    setup_requires=['pytest-runner'],
)
