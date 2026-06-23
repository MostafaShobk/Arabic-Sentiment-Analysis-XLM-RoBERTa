

from setuptools import setup, find_packages

# Function to read requirements from requirements.txt
def parse_requirements(filename):
    with open(filename, 'r') as f:
        lines = (line.strip() for line in f)
        requirements = [line for line in lines if line and not line.startswith('#')]
    return requirements

setup(
    name='sentiment-analysis-library',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=parse_requirements('requirements.txt'),
    # Add other setup options as needed
)
