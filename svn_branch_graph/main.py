#!/usr/bin/env python

import ConfigParser
import json
import os.path
import re
import subprocess
import sys
import xml.etree.ElementTree

import web

import cache

config = ConfigParser.RawConfigParser()
config.read('svn_branch_graph.cfg')

server_url = config.get('svn', 'server-url')

branches_path = config.get('svn', 'branches-path')
trunk_path = config.get('svn', 'trunk-path')

username = config.get('svn', 'username')
password = config.get('svn', 'password')

cut_off_point = int(config.get('graph', 'cut-off-point'))

cache_enabled = False
if config.has_section('cache'):
    cache_enabled = config.get('cache', 'enable') == 'True'
    if cache_enabled:
        cache_database = cache.CacheSqlite3Database(
                config.get('cache', 'sqlite3-path'),
                int(config.get('cache', 'refresh')),
                )
        cache_database.dbinit()

def call(cmd):
    if cache_enabled:
        cache_database = cache.CacheSqlite3Database(
                config.get('cache', 'sqlite3-path'),
                int(config.get('cache', 'refresh')),
                )
        stdout = cache_database.get(json.dumps(cmd))
        if stdout:
            return 0, stdout
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if p.returncode == 0 and cache_enabled:
        cache_database.cache(json.dumps(cmd), stdout)
    return p.returncode, stdout

def get_svn_ls(svn_branches_url):
    command = ['svn', 'ls', '--non-interactive', svn_branches_url]
    if username:
        command.extend(['--username', username])
    if password:
        command.extend(['--password', password])
    return_code, stdout = call(command)
    if return_code != 0:
        raise RuntimeError('svn ls %s failed.' % svn_branches_url)
    return stdout.splitlines()

def get_svn_log(svn_branch_url):
    command = ['svn', 'log', '--non-interactive', '-v',
        '--xml', '--stop-on-copy', svn_branch_url]
    if username:
        command.extend(['--username', username])
    if password:
        command.extend(['--password', password])
    return_code, stdout = call(command)
    if return_code != 0:
        raise RuntimeError('svn log %s failed.' % svn_branch_url)
    root = xml.etree.ElementTree.fromstring(stdout)
    svn_log = []
    for logentry in root.findall('logentry'):
        log = {}
        log['revision'] = int(logentry.get('revision'))
        log['author'] = logentry.findtext('author')
        log['msg'] = logentry.findtext('msg')
        # date looks like this: 2010-10-11T11:03:25.847546Z
        log['date'] = logentry.findtext('date').split('.')[0].replace('T', ' ')
        svn_log.append(log)
    copyfrom = None
    for path in logentry.findall('paths/path'):
        if path.get('copyfrom-rev'):
            copyfrom_path = path.get('copyfrom-path')
            copyfrom_rev = path.get('copyfrom-rev')
            command = ['svn', 'log', '--xml', '--limit=1', '%s%s@%s' % (
                server_url, copyfrom_path, copyfrom_rev)]
            if username:
                command.extend(['--username', username])
            if password:
                command.extend(['--password', password])
            return_code, stdout = call(command)
            log = xml.etree.ElementTree.fromstring(stdout)
            copyfrom = int(log.find('logentry').get('revision'))
    svn_log.reverse()
    return svn_log, copyfrom


class Index(object):
    def GET(self):
        """Returns the main page of svn branch graph, with a list of
        checkboxes to select which branches
        """
        branches = get_svn_ls('%s%s' % (server_url, branches_path))
        # only include folders
        branches = [b.strip('/') for b in branches if b.endswith('/')]
        return render.index(
                server_url,
                trunk_path,
                branches_path,
                branches,
                )


class GetGraph(object):
    def GET(self):
        """Returns the svn branch graph with all the branches

        :Parameters:
          - `branch`: list of branch names
        """
        i = web.input(branch=[], branch_regexp='')

        if i.branch_regexp:
            pattern = re.compile('%s/?$' % i.branch_regexp)
            branches = get_svn_ls('%s%s' % (server_url, branches_path))
            branches = ['%s/%s' % (branches_path, b.strip('/'))
                    for b in branches if pattern.match(b)]
            if pattern.match('trunk'):
                branches.append(trunk_path)
        else:
            branches = i.branch

        svn_logs = []
        copyfromlist = {}
        for branch in branches:
            logs, copyfrom = get_svn_log('/'.join([server_url, branch]))
            if branch == trunk_path:
                readable = 'trunk'
            else:
                readable = branch.replace(branches_path, '').strip('/')
            for log in logs:
                log['branch'] = readable
            copyfromlist[readable] = copyfrom
            svn_logs.extend(logs)
        svn_logs.sort(lambda a, b: cmp(a['revision'], b['revision']))

        if svn_logs:
            initial_branch = svn_logs[0]['branch']
            index = 0
            for i, log in enumerate(svn_logs):
                if log['branch'] != initial_branch:
                    index = i
                    break
            if index > cut_off_point:
                svn_logs = svn_logs[index - cut_off_point:]

        changeset_url = None
        if config.has_section('changeset'):
            changeset_url = config.get('changeset', 'url')
        return render.graph(
                json.dumps(changeset_url),
                urls[0],
                branches,
                json.dumps(svn_logs).replace('\\', '\\\\'),
                json.dumps(copyfromlist).replace('\\', '\\\\'),
                )


urls = (
        '/', 'Index',
        '/get-graph', 'GetGraph',
        )

render = web.template.render(os.path.join(os.path.dirname(__file__),
    'templates'))

def main():
    app = web.application(urls, globals())
    app.run()

if __name__ == '__main__':
    main()
