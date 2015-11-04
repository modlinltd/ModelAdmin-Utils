from setuptools import setup, find_packages
import modeladmin_utils


setup(
    name='django-modeladmin-utils',
    author='Pavel Savchenko',
    author_email='pavel@modlinltd.com',
    url='http://modlinltd.com/',
    version=modeladmin_utils.__version__,
    packages=find_packages(),
    description='ModelAdmin utils',
    install_requires=['django>=1.4'],
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.4',
        'Framework :: Django :: 1.5',
        'Framework :: Django :: 1.6',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
)
