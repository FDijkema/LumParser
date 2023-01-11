from distutils.core import setup
from setuptools import find_packages


setup(
name='lumparser',
packages=find_packages("src"),
package_dir={'': 'src'},
version='0.0.3',
include_package_data=True,
requires=['numpy', 'scipy', 'matplotlib']
)
