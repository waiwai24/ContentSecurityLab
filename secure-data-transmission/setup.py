from setuptools import setup, find_packages

setup(
    name='secure-data-transmission',
    version='0.1.0',
    author='Student',
    author_email='student@example.com',
    description='A project for secure data transmission using public channels with data hiding and fragmentation.',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'numpy',
        'opencv-python',
        'Pillow',
        'requests',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)