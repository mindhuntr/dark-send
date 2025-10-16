from setuptools import setup, find_packages

with open("README.md", "r") as f: 
    long_description = f.read()

setup(
    name="dark-send",
    version="1.2.0",
    description="A Command Line Interface for Telegram",
    author="Irfan Jalal",
    author_email="mindhunter@blinkenshell.org",
    url="https://github.com/mindhuntr/dark-send",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires = [
        "hachoir>=3.3.0",
        "InquirerPy>=0.3.4",
        "telethon>=1.37.0",
        "tqdm>=4.60.0",
    ],
    entry_points={
        "console_scripts": [
            "dark-send=dark_send.cli:entrypoint",
        ],
    },

    classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    ],

    python_requires=">=3.8",
)

