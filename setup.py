from setuptools import setup, find_packages

def long_description(source):
    with open(source, 'r') as f:
        return f.read()

setup(
    name = "url_gatekeeper",
    version = "0.1.1",
    author = "Sheepdog",
    author_email = "development@sheepdoginc.ca",
    description = ("Opt-out permission restrictions by URL patterns"),
    license = "BSD",
    keywords = "permissions URL",
    url = "https://github.com/SheepDogInc/django-versioning",
    packages=find_packages(),
    long_description=long_description("README.md"),
    include_package_data=True,
)

