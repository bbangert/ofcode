try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


setup(
    name='ofcode',
    version='0.1',
    description='paste.ofcode.org site',
    author='',
    author_email='',
    url='',
    install_requires=[
        "gunicorn>=0.13.4",
        "pyramid>=1.3a5",
        "Pygments>=1.4",
        "docutils>=0.8.1",
        "redis>=2.4.11",
        "hiredis>=0.1.0",
        "pyramid-debugtoolbar>=0.9.8",
        "waitress>=0.7",
        "formencode>=1.2.4",
        "simplejson>=2.3.2",
        "decorator>=3.3.2",
        "webhelpers>=1.3",
    ],
    setup_requires=["PasteScript>=1.7.5"],
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
