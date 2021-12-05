from setuptools import setup, find_packages

setup(
    name='insurance-db',
    version='0.0.1rc2',
    packages=find_packages(include=['insurancedb', 'insurancedb.*']),
    url='',
    install_requires=['pdfplumber==0.5.28', 'pandas', 'click>=8.0.1'],
    entry_points={
        'console_scripts': ['insurance-db=insurancedb.main:create_db_parallel']
    },
    license='MIT',
    author='ionatanfrim',
    author_email='ionatanfrim@gmail.com',
    description='insurance db from RO insurance pdf files'
)

# ImageMagick https://docs.wand-py.org/en/latest/guide/install.html#
# tesseract https://digi.bib.uni-mannheim.de/tesseract/
