from setuptools import setup, find_packages

setup(
    name="dark-send",
    version="0.1.0",
    description="A CLI telegram tool",
    author="Irfan Jalal",
    author_email="mindhunter@blinkenshell.org",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "hachoir==3.3.0",
        "InquirerPy==0.3.4",
        "rich==14.1.0",
        "telethon==1.40.0",
        "tqdm==4.67.1",
    ],
    entry_points={
        "console_scripts": [
            "dark-send=dark_send.cli:entrypoint",
        ],
    },
    python_requires=">=3.7",
)

