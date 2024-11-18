from setuptools import setup, find_packages

setup(
   name='barebonesllmchat',
   version='0.0.0',
   description='A useful module',
   author='Man Foo',
   author_email='foomail@foo.example',
    packages=find_packages(),
   #packages=['chatbot', 'common', 'server', 'terminal'],  #same as name
   #install_requires=['wheel', 'bar', 'greek'], #external packages as dependencies
)


