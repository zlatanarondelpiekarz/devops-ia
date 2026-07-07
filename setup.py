from setuptools import find_packages, setup

setup(
    name="gitlab-rules-manager",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "gitlab-rules=app.apply_rules:main",
        ],
    },
    python_requires=">=3.12",
)
