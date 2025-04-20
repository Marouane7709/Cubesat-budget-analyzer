from setuptools import setup, find_packages

setup(
    name="cubesat-budget-analyzer",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "PyQt6>=6.4.0",
        "SQLAlchemy>=2.0.0",
        "matplotlib>=3.7.0",
        "pyqtgraph>=0.13.0",
        "reportlab>=4.0.0",
        "pandas>=2.0.0",
        "openpyxl>=3.1.0",
        "pyinstaller>=5.10.0"
    ],
    entry_points={
        'console_scripts': [
            'cubesat-budget=run:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A desktop application for analyzing CubeSat link and data budgets",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Marouane7709/cube_sat_budget",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
) 