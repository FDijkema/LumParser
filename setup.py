from distutils.core import setup
from setuptools import find_namespace_packages


setup(
    name='lumparser',
    packages=find_namespace_packages(where="src"),
    package_dir={'': 'src'},
    version='0.0.4',
    include_package_data=True,
    requires=['numpy', 'scipy', 'matplotlib']
)
