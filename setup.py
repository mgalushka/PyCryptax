import setuptools

setuptools.setup(
    name="StocksTax",
    version="1.0.1",
    author="Maxim Galushka",
    author_email="maxim.galushka@mail.ru",
    description="Program to compute PnL for tax purposes",
    long_description="Program to compute PnL for tax purposes",
    long_description_content_type="text/markdown",
    url="https://github.com/mgalushka/StocksTax",
    packages=['pycryptax'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)