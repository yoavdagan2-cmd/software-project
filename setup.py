from setuptools import setup, Extension

module = Extension("mykmeanssp", sources=["kmeansmodule.c"])

setup(
    name="mykmeanssp",
    version="1.0",
    description="K-means C extension for HW2",
    ext_modules=[module],
)