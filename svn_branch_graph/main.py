#!/usr/bin/env python

import ConfigParser
import json
import os.path
import subprocess
import sys
import xml.etree.ElementTree

import web

def call(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return p.returncode, stdout

config = ConfigParser.RawConfigParser()
config.read('svn_branch_graph.cfg')

def get_branch_url():
    svn_branches_url = '%s%s' % (config.get('svn', 'server-url'),
            config.get('svn', 'branches-path', 'branches'))

    return svn_branches_url

def get_svn_ls(svn_branches_url):
    return_code, stdout = call(['svn', 'ls', svn_branches_url])
    if return_code != 0:
        raise RunTimeError('svn ls %s failed.' % svn_branches_url)
    return stdout.splitlines()

def get_svn_log(svn_branch_url):
    return_code, stdout = call(['svn', 'log', '--xml', '--stop-on-copy',
        svn_branch_url])
    if return_code != 0:
        raise RunTimeError('svn log %s failed.' % svn_branch_url)
    root = xml.etree.ElementTree.fromstring(stdout)
    svn_log = []
    for logentry in root.findall('logentry'):
        log = {}
        log['revision'] = logentry.get('revision')
        log['author'] = logentry.findtext('author')
        log['msg'] = logentry.findtext('msg')
        svn_log.append(log)
    return svn_log

BRANCH_COOKIE = 'svn-branches'


class Index(object):
    def GET(self):
        """Returns the main page of svn branch graph, with a list of
        checkboxes to select which branches
        """
        selected_branches = web.cookies().get(BRANCH_COOKIE)

        svn_branches_url = get_branch_url()
        branches = get_svn_ls(svn_branches_url)
        # only include folders
        branches = [b.strip('/') for b in branches if b.endswith('/')]
        return render.index(
                svn_branches_url,
                branches,
                selected_branches,
                )


class GetGraph(object):
    def GET(self):
        """Returns the svn branch graph with all the branches

        :Parameters:
          - `branch`: list of branch names
        """
        i = web.input(branch=[])
        # cookie lasts for a week
        web.setcookie('svn-branches', i.branch, 3600 * 24 * 7)
        svn_branch_url = get_branch_url()
        svn_logs = {}
        revisions = []
        for branch in i.branch:
            svn_logs[branch] = get_svn_log('/'.join([svn_branch_url, branch]))
            revisions.extend([x['revision'] for x in svn_logs[branch]])
        revisions.sort()
        return render.graph(
                i.branch,
                json.dumps(svn_logs),
                json.dumps(revisions),
                )


urls = (
        '/', 'Index',
        '/get-graph', 'GetGraph',
        )

app = web.application(urls, globals())
render = web.template.render(os.path.join(os.path.dirname(__file__),
    'templates'))

def main():
    app.run()

if __name__ == '__main__':
    main()
