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

DEPLOY AS APACHE CGI
--------------------
    Create a cgi directory::

        mkdir /var/www/cgi

    Create svn_branch_graph in your cgi directory::

        import svn_branch_graph.main
        svn_branch_graph.main.main()

    Make svn_branch_graph executable::

        chmod a+x svn_branch_graph

    Add this in your apache config file::

        ScriptAlias /path-you-like/ /var/www/cgi/
        <Directory "/var/www/cgi">
            Options +ExecCGI
        </Directory>

    Restart apache and go to
    http://hostname/path-you-like/svn_branch_graph/ in Firefox to use
    the application.
