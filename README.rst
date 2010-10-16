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
        trunk-path = trunk
        username = username
        password = password

    If you want caching enabled, please create an empty sqlite3 database and add
    this in svn_branch_graph.cfg::

        [cache]
        enable = True
        sqlite3-path = svn_branch_graph_cache.sqlite3
        refresh = 15

    refresh is how long in minutes until cache expire.  The sqlite3 database
    needs to be writeable by the user executing the script and the user needs
    read, write, execute permissions on the directory containing the sqlite3
    database.

    Configure the changeset url by adding this in svn_branch_graph.cfg::

        [changeset]
        url = http://svnserver/changeset/%s

    where %s is where the revision will go.

    Configure the number of commits to display before the first branch::

        [graph]
        cut-off-point = 10
