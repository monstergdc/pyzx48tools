
from setuptools import setup, find_packages

setup(
    name="pyzx48tools",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pillow",  # PIL comes from the "pillow" package
    ],
    author="Jakub Noniewicz aka MoNsTeR/GDC",
    author_email="JNoniewicz@gmail.com",
    description="ZX Spectrum data manipulation tools",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/monstergdc/pyzx48tools",
    license="LGPL-3.0-or-later"
,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
