from setuptools import setup, find_packages

setup(
    name='insurance-db',
    version='0.0.3rc1',
    packages=find_packages(include=['insurancedb', 'insurancedb.*']),
    url='',
    install_requires=['pdfplumber==0.5.28', 'pandas', 'click>=8.0.1', 'pytesseract==0.3.8', 'pillow==8.4.0',
                      'opencv-python>=4.5.5', 'numpy>=1.21'],
    entry_points={
        'console_scripts': ['insurance-db=insurancedb.main:create_db_parallel']
    },
    license='MIT',
    package_data={'': ['resources/*.*']},
    include_package_data=True,
    author='ionatanfrim',
    author_email='ionatanfrim@gmail.com',
    description='insurance db from RO insurance pdf files'
)

# ImageMagick https://docs.wand-py.org/en/latest/guide/install.html#  ImageMagick 7.1.0-16 Q16-HDRI
# tesseract https://digi.bib.uni-mannheim.de/tesseract/ 5.0.1
# https://www.ghostscript.com/releases/gsdnld.html 9.55.0
