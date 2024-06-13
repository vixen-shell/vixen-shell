"""
Author            : Nohavye
Author's Email    : noha.poncelet@gmail.com
Repository        : https://github.com/vixen-shell/vixen-shell.git
Description       : pip setup file.
License           : GPL3
"""

from setuptools import setup, find_packages

setup(
    name="vx_libraries",
    version="1.0.0b1",
    description="Vixen Shell Libraries",
    packages=find_packages(),
    url="https://github.com/vixen-shell/vixen-shell.git",
    license="GPL3",
    author="Nohavye",
    author_email="noha.poncelet@gmail.com",
    python_requires=">=3.11.7",
)
