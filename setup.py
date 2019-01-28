from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='optommp',
        version='0.2',
        description='Python toolkit for Opto 22 memory-mapped devices',
        long_description=long_description,
        url='http://github.com/optodeveloper/optommp',
        download_url='https://github.com/optodeveloper/optommp/archive/v0.2.tar.gz',
        license='mit',
        author='Opto 22',
        author_email='torchard@opto22.com',
        packages=['optommp'],
        zip_safe=False,
        classifiers=[
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 2.7'
            ])
