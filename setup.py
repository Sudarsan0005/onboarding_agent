from setuptools import setup,find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="Onboarding Agent",
    version="0.1",
    author="Sudarsan Parida",
    packages=find_packages(),
    install_requires = requirements,
)
# for installing packages
## pip install -e .
