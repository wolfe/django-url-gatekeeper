from setuptools import setup, find_packages

def long_description(source):
    with open(source, 'r') as f:
        return f.read()

setup(
    name = "django-url-gatekeeper",
    version = "0.1.2",
    author = "Sheepdog",
    author_email = "development@sheepdoginc.ca",
    description = ("Opt-out permission restrictions by URL patterns"),
    license = "BSD",
    keywords = "permissions URL",
    url = "https://github.com/SheepDogInc/django-url-gatekeeper",
    packages=find_packages(exclude=["example"]),
    long_description=long_description("README.md"),
    include_package_data=True,
)

