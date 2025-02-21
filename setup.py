from setuptools import setup, find_packages
setup(name='AICertify', version='0.1', packages=find_packages(),
package_data={
'aicertify': ['fonts/.ttf'],
},
include_package_data=True,)
