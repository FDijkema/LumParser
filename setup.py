from distutils.core import setup


setup(
name='lumparser',
packages=["lumparser"],
package_dir={'': 'src'},
version='0.0.1',
include_package_data=True,
requires=['numpy', 'scipy', 'matplotlib']
)
