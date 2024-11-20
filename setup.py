from setuptools import setup, find_packages

setup(
    name="nanoelectropore-gui",
    version="0.1.0",
    description="GUI controls and interface for Quantum-NanoElectroPore controller.",
    author="Brendan Waldrop",
    author_email="bwwaldr1@asu.edu",
    packages=find_packages(),
    install_requires=[
        "setuptools",
        "PySide6",
        "pyqtgraph",
        "numpy",
    ],
    entry_points={
        "console_scripts": [
            "nanogui=nanogui.gui:run",
        ]
    },
    python_requires=">=3.12",
)