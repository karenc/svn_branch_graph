NAME
----
    svn branch graph

DESCRIPTION
-----------
    Displays a simple graph of svn commits of different branches

HOW TO INSTALL
--------------
    ::

        python setup.py install

HOW TO USE
----------
    Running svn_branch_graph will start a web server listening on port 8080,
    the host and port to listen on can be specified like this::

        svn_branch_graph 127.0.0.1:8000

    Go to http://hostname:8080/ in Firefox to use the application.

CONFIGURATION
-------------
    Please configure your svn repo url in svn_branch_graph.cfg, which should be
    in the current directory when running svn_branch_graph::

        [svn]
        server-url = http://svnserver/repo/
        branches-path = branches

