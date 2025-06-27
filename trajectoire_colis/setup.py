from setuptools import setup, find_packages

setup(
    name='trajectoire_colis',
    version='0.1.0',
    author='Linda Ghazouani, Syrine Boudef, Wilson David Parra Oliveros',
    description='Simulation de la trajectoire d’un parachute guidé avec prise en compte du vent',
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'numpy',
        'requests',
        'cvxpy',
        'matplotlib',
        'streamlit'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
