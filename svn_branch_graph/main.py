#!/usr/bin/env python

import ConfigParser
import json
import os.path
import re
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

server_url = config.get('svn', 'server-url')

branches_path = config.get('svn', 'branches-path')
if not branches_path:
    branches_path = 'branches'

def get_branch_url():
    svn_branches_url = '%s%s' % (server_url, branches_path)
    return svn_branches_url

def get_svn_ls(svn_branches_url):
    return_code, stdout = call(['svn', 'ls', svn_branches_url])
    if return_code != 0:
        raise RunTimeError('svn ls %s failed.' % svn_branches_url)
    return stdout.splitlines()

def get_svn_log(svn_branch_url):
    return_code, stdout = call(['svn', 'log', '-v', '--xml', '--stop-on-copy',
        svn_branch_url])
    if return_code != 0:
        raise RunTimeError('svn log %s failed.' % svn_branch_url)
    root = xml.etree.ElementTree.fromstring(stdout)
    svn_log = []
    for logentry in root.findall('logentry'):
        log = {}
        log['revision'] = int(logentry.get('revision'))
        log['author'] = logentry.findtext('author')
        log['msg'] = logentry.findtext('msg')
        svn_log.append(log)
    copyfrom = None
    for path in logentry.findall('paths/path'):
        if path.get('copyfrom-rev'):
            copyfrom_path = path.get('copyfrom-path')
            copyfrom_rev = path.get('copyfrom-rev')
            return_code, stdout = call(['svn', 'log', '--xml', '--limit=1',
                '%s%s@%s' % (server_url, copyfrom_path, copyfrom_rev)])
            log = xml.etree.ElementTree.fromstring(stdout)
            copyfrom = int(log.find('logentry').get('revision'))
    svn_log.reverse()
    return svn_log, copyfrom

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
        i = web.input(branch=[], branch_regexp='')
        # cookie lasts for a week
        web.setcookie('svn-branches', i.branch, 3600 * 24 * 7)
        svn_branch_url = get_branch_url()

        if i.branch_regexp:
            pattern = re.compile(i.branch_regexp)
            branches = get_svn_ls(svn_branch_url)
            branches = [b.strip('/') for b in branches if pattern.match(b)]
        else:
            branches = i.branch

        svn_logs = []
        copyfromlist = {}
        for branch in branches:
            logs, copyfrom = get_svn_log('/'.join([svn_branch_url, branch]))
            copyfromlist[branch] = copyfrom
            for log in logs:
                log.setdefault('branch', branch)
            svn_logs.extend(logs)
        svn_logs.sort(lambda a, b: cmp(a['revision'], b['revision']))
        return render.graph(
                branches,
                json.dumps(svn_logs).replace('\\', '\\\\'),
                json.dumps(copyfromlist).replace('\\', '\\\\'),
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