
class Git(object):
    def __init__(self, local, m, remote_url=None):

        super().__init__()

        from ..util.locations import locate_file

        if callable(m): self.m = m
        else: raise Exception('wrong m(')

        self.__local = locate_file(local, create_in=local)
        self.__remote_url = remote_url

        if not self._log(num=0, critical=False).get('returncode', False) == 0:
            if not self.remote_url: self.m('a new git clone without remote url is not possible. sorry', state=True, more=dict(local=self.local))
            self.m(
                'cloning into repo',
                cmdd=dict(cmd='git clone %s %s' %(self.remote_url, self.local))
            )

        self.m('git tool startup done', more=dict(remote_url=self.remote_url, local=self.local), verbose=False)

    @property
    def local(self):

        return self.__local

    @property
    def remote_url(self):

        return self.__remote_url

    @property
    def remote(self):

        return self._remote_show().get('out')


    @property
    def commit(self):

        return self._log(num=1, format='%H').get('out')


    @property
    def log(self):

        log = self._log(num=10, format='%h::%b').get('stdout')
        if log: return [dict(commit=c, message=m) for c, m in [l.split('::') for l in log]]

    @property
    def status(self):

        status = self.m(
            'getting git status',
            cmdd=dict(cmd='git status --porcelain', cwd=self.local),
            verbose=False
        ).get('stdout')
        o, m, f, g = list(), list(), list(), list()
        if status:
            for w in status:
                s, t = w[:2], w[3:]
                if '?' in s: o.append(t)
                if 'M' in s: m.append(t)
                if 'D' in s: f.append(t)
                if 'U' in s: g.append(t)
        clean = False if o + m + f + g else True
        return dict(untracked=o, modified=m, deleted=f, conflicting=g, clean=clean)

    @property
    def branch(self):

        branch = self._branch_show().get('stdout')
        if branch: return ''.join([b for b in branch if '*' in b]).replace('*', '').strip()

    @branch.setter
    def branch(self, branch):

        if not branch: branch = 'master'
        tracking = '' if branch in self._branch_show(remotes=True).get('out') else '-B '
        self.m(
            'checking out branch',
            cmdd=dict(cmd='git checkout %s%s' %(tracking, branch), cwd=self.local)
        )
        return self.branch

    @property
    def cleanup(self):

        from photon import __ident__
        from ..util.system import get_hostname

        hostname = get_hostname()
        old_branch = self.branch

        changes = self.status
        if not changes.get('clean'):

            self.branch = hostname

            for f in changes.get('untracked', []) + changes.get('modified', []):
                self.m(
                    'adding file to repository',
                    cmdd=(dict(cmd='git add %s' %(f), cwd=self.local)),
                    more=f
                )
            for f in changes.get('deleted', []):
                self.m(
                    'deleting file from repository',
                    cmdd=(dict(cmd='git rm %s' %(f), cwd=self.local)),
                    more=f
                )
            if changes.get('conflicting'): self.m('you have conflicting files in your repository!', state=True, more=changes)

            self.m(
                'auto commiting changes',
                cmdd=dict(cmd='git commit -m "%s %s auto commit"' %(hostname, __ident__), cwd=self.local),
                more=changes
            )

        self.branch = old_branch

        fetch = self.m(
            'fetching remote changes',
            cmdd=dict(cmd='git fetch --tag', cwd=self.local)
        )

        if 'CONFLICT' in fetch.get('out'): self.m('you have a merge conflict with your remote repository!', state=True, more=fetch)
        if fetch.get('stdout'):
            self.m(
                'merging with remote changes',
                cmdd=dict(cmd='git merge master -m "%s %s auto merge"' %(hostname, __ident__), cwd=self.local),
                more=fetch
            )

        return dict(changes=changes, fetch=fetch)

    @property
    def publish(self):

        self.cleanup

        remote = self.remote
        branch = self.branch
        return self.m(
            'pushing changes to %s/%s' %(remote, branch),
            cmdd=dict(cmd='git push -u %s %s' %(remote, branch), cwd=self.local),
            more=dict(remote=remote, branch=branch)
        )

    def _remote_show(self, cached=True):

        return self.m(
            'getting current remote',
            cmdd=dict(cmd='git remote show %s' %('-n' if cached else ''), cwd=self.local),
            verbose=False
        )

    def _log(self, num=None, format=None, critical=True):

        num = '-n %s' %(num) if num else ''
        format = '--format="%s"' %(format) if format else ''
        return self.m(
            'getting git log',
            cmdd=dict(cmd='git log %s %s' %(num, format), cwd=self.local),
            critical=critical,
            verbose=False
        )

    def _branch_show(self, remotes=None):

        return self.m(
            'getting git branch information',
            cmdd=dict(cmd='git branch %s' %('-r' if remotes else ''), cwd=self.local),
            verbose=False
        )
