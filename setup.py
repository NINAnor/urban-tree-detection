from setuptools import find_packages, setup

requirements = [
    # package requirements go here
]

setup(
    name='src',
    version='0.1.0',
    description="This project provides a workflow for preparing an input dataset for i-Tree Eco analysis using a municipal tree dataset supplemented with lidar-segmented tree crown geometry and auxiliary GIS datasets. ",
    license="MIT",
    author="willeke acampo",
    author_email='willeke.acampo@nina.no',
    url='https://github.com/ac-willeke/urban-treeDetection',
    packages=find_packages(),
    
    install_requires=requirements,
)