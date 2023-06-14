import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="merge_image_metadata",
    version="0.0.1",
    author="Jonas A. Wendorf",
    description="Merges image metadata (Keywords, Subject, HierarchicalSubject) as used by Adobe Bridge between images",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jonasw234/merge_image_metadata",
    packages=setuptools.find_packages(),
    install_requires=["imagehash", "Pillow"],
    include_package_data=True,
    classifiers=[
        "Environment :: Console",
        "Natural Language :: English",
        "OSI Approved :: GNU General Public License v3 or later (GPLv3)",
        "Operating System :: Windows",
        "Programming Language :: Python :: 3",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Utilities",
    ],
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "merge_image_metadata=merge_image_metadata.merge_image_metadata:main"
        ],
    },
)
