from setuptools import setup
import subprocess as sp

def get_version() :
    try : 
        version = sp.check_output(["git", "describe"])
        return version.decode().strip().replace("-g", "+g")
    except sp.CalledProcessError : 
        return "V0.1"

setup(
    name="snakeutils",
    version=get_version(),
    author="Luka PAVAGEAU",
    packages=["snakeutils"],
    scripts=["snakeutils/snakebench.py"],
    install_requires=["pandas=1", "plotly=6"],
)
