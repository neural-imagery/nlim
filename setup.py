from setuptools import find_packages, setup

with open("VERSION") as f:
    version = f.read()

setup(
    name="aslflash",
    version=version,
    description="Neural Imagery Backend",
    author="Neural Imagery Team",
    url="neuralimagery.com",
    packages=find_packages(),
)
