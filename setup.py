from setuptools import setup, find_packages

setup(
    name='ofcode',
    version='0.4',
    description='paste.ofcode.org site',
    author='',
    author_email='',
    url='',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={},
    zip_safe=False,
    paster_plugins=['PasteScript'],
    entry_points="""
    [paste.app_factory]
    main = ofcode:main
    """,
)
