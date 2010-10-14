from setuptools import setup

setup(
        name='svn_branch_graph',
        version='0.1',
        author='Karen Chan',
        author_email='karen.chan@isotoma.com',
        license='BSD',
        packages=['svn_branch_graph'],
        package_data={
            'svn_branch_graph': ['templates/*'],
            },
        include_package_data=True,
        install_requires=[
            'web.py',
            ],
        entry_points = {
            'console_scripts': ['svn_branch_graph = svn_branch_graph.main:main'],
            },
        )
