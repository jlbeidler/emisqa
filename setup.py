from distutils.core import setup
setup(
    name="emisqa",
    version="0.3.1",
    packages=['emisqa','emisqa.camx','emisqa.cmaq','emisqa.csv','emisqa.dataout','emisqa.dateloop','emisqa.inline','emisqa.runtypes'],
    scripts = ['bin/emisqa',],
    package_data = {'emisqa': ['ancillary/*','ancillary/2016/*']}, 
    python_requires='>3.5',
    setup_requires=['numpy>=1.12,<=1.24.3','netCDF4>=1.2.9,<=1.5.8','pandas>=0.20,<1','fauxioapi>=0.1.5'],
    author_email='james.beidler@gmail.com'
)
