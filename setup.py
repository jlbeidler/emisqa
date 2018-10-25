from setuptools import setup, find_packages

setup(
    name="emisqa",
    version="0.1",
    packages=['fauxioapi'],
    package_dir = {'': 'src'},
    scripts = ['src/emisqa.py',]
    python_requires='>3.5',
    setup_requires=['numpy>=1.12','netCDF4>=1.2.9'],
    author_email='james.beidler@gmail.com'
)
