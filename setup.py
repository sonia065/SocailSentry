---

## 4. `setup.py`

```python
from setuptools import setup, find_packages

setup(
    name="socialsentry",
    version="1.0.0",
    description="Authorized Social Media Security Assessment Toolkit",
    author="Security Researcher",
    author_email="research@example.com",
    url="https://github.com/yourusername/SocialSentry",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "colorama>=0.4.6",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "socialsentry=socialsentry.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Information Technology",
        "Topic :: Security :: Penetration Testing",
    ],
    python_requires=">=3.8",
)
