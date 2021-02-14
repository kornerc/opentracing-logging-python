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
    install_requires=['opentracing>=2.1,<3.0'],
    tests_require=['pytest'],
    setup_requires=['pytest-runner'],
    keywords=['opentracing', 'logging'],
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
