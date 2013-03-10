from distutils.core import setup

setup(
    name='duo_python',
    version='0.1.0',
    author='DuoSecurity',
    author_email='duo@duosecurity.com',
    packages=['duo_web',],
    scripts=[],
    package_data={
        'duo_web': [
            'js/*.js',
        ],
    },
    data_files=[
        ( 'js', 
            [
                'js/Duo-Web-v1.bundled.js',
                'js/Duo-Web-v1.bundled.min.js',
                'js/Duo-Web-v1.js',
                'js/Duo-Web-v1.min.js',
            ],
        ),
    ],
    url='https://github.com/duosecurity/duo_python',
    license='LICENSE.txt',
    description='Duo two-factor authentication for Python web applications',
    long_description=open('README').read(),
    install_requires=[],
)