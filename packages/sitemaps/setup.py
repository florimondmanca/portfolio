from setuptools import setup

setup(
    name="sitemaps",
    version="0.1.0",
    description="Sitemap generation for Python async web apps.",
    author="Florimond Manca",
    author_email="florimond.manca@gmail.com",
    py_modules=["sitemaps"],
    install_requires=["httpx"],
    python_requires=">=3.7",
    license="MIT",
)
