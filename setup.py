from setuptools import setup, find_packages

setup(
    name='insurance-db',
    version='0.0.1rc1',
    packages=find_packages(include=['insurancedb', 'insurancedb.*']),
    url='',
    install_requires=['pdfplumber','pandas','click>=8.0.1'],
    entry_points={
        'console_scripts': ['insurance-db=insurancedb.main:create_db']
    },
    license='MIT',
    author='ionatanfrim',
    author_email='ionatanfrim@gmail.com',
    description='insurance db from RO insurance pdf files'
)
