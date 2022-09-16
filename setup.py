from setuptools import setup, find_packages

requirements = [

]

setup(
    name='text-concept-evaluator',
    version='0.1.0',
    description='Generates keywords by evaluating the statistics of an annotated text.',
    license="AGPLv3",
    long_description='',
    long_description_content_type="text/markdown",
    author='Adrian Pachzelt',
    author_email='a.pachzelt@ub.uni-frankfurt.de',
    url="https://www.biofid.de",
    download_url='https://github.com/FID-Biodiversity/text-concept-evaluator',
    python_requires='>=3.8',
    packages=find_packages(exclude='tests'),
    install_requires=requirements,
    extras_require={
        'dev': [
            'black',
            'pytest',
        ]
    }
)
