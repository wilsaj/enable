from setuptools import setup, find_packages

setup(
    name = 'enthought.enable2',
    version = '2.1.0',
    description  = 'Kiva-based GUI Window and Component package',
    author       = 'Enthought, Inc',
    author_email = 'info@enthought.com',
    url          = 'http://code.enthought.com/ets',
    license      = 'BSD',
    zip_safe     = False,
    packages = find_packages(),
    include_package_data = True,
    install_requires = [
        "numpy",
        "enthought.kiva",
        "enthought.traits",
    ],
    extras_require = {
        "wx": ["enthought.traits.ui.wx"],
    },
    namespace_packages = [
        "enthought",
    ],
)
