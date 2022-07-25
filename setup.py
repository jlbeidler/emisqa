from setuptools import setup, find_packages
setup(
    name="emisqa",
    version="0.2",
    packages=find_packages(),
    scripts = ['bin/emisqa',],
    package_data = {'emisqa': ['ancillary/*','ancillary/2016/*']}, 
    python_requires='>3.5',
    setup_requires=['numpy>=1.12','netCDF4>=1.2.9','pandas>=0.20'],
    author_email='james.beidler@gmail.com'
)
