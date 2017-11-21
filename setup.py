from setuptools import setup

if __name__ == "__main__":
    setup(
        name="jasmin-arc-py",
        description="Library to submit and manage jobs on LOTUS on JASMIN via the ARC-CE server",
        url="https://github.com/cedadev/jasmin-arc-py",
        author="CEDA",
        keywords="jasmin lotus arc arc-ce",
        packages=["jasmin_arc"],
        version="0.1",
        install_requires=[
            "Jinja2",
            "enum34"
        ],
        license="BSD",
    )
