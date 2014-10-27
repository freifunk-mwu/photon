#!/usr/bin/env python3

def _p(s): print(s)
def _pp(s):
    from pprint import pformat
    return _p(pformat(s))
def _j(s):
    from json import dumps
    return _p(dumps(s, indent=4, sort_keys=True))
def _y(s):
    from yaml import dump
    return _p(dump(s, indent=4, default_flow_style=False))
def _t(s, p=0):
    if isinstance(s, str): return _p('%s%s' %('\t'*p, s))
    if isinstance(s, list): return [_t(t, p) for t in s]
    if isinstance(s, dict):
        for t, u in sorted(s.items()):
            _t(t, p)
            _t(u, p+1)
        return

FTYPES = {'j': _j, 'p': _p, 'pp': _pp, 't': _t, 'y': _y}

def fmt(structure, ftype):
    if ftype in FTYPES.keys():
        FTYPES[ftype](structure)

def args():
    from argparse import ArgumentParser
    p = ArgumentParser(
        prog='photon settings tool',
        description='reads photon settings files to display and/or save the output',
        epilog='-.-',
        add_help=True
    )
    p.add_argument('--defaults', '-d', action='store', default='defaults.yaml', help='specify defaults file to load')
    p.add_argument('--config', '-c', action='store', default=None, help='specify config file to load and writeback')
    p.add_argument('--formatter', '-f', action='store', default='pp', choices=sorted(FTYPES.keys()), help='Use a formatter to print. Choose between p_rint p_retty_p_rint (default), j_son, y_aml or nested t_abs')
    p.add_argument('--verbose', '-v', action='store_true', default=False, help='show info and warn messages')
    p.add_argument('setting', nargs='*', help='space separated list into settings')
    return p.parse_args()

def main(defaults, setting, config=None, verbose=True):
    from photon import Settings
    res = Settings(defaults=defaults, config=config, verbose=verbose).get
    for s in setting:
        if s in res: res = res[s]
        else: return False
    return res

if __name__ == '__main__':
    from os import sep, path
    a = args()

    if a.config and sep in a.config: a.config = path.abspath(path.expanduser(a.config))

    fmt(main(defaults=a.defaults, setting=a.setting, config=a.config, verbose=a.verbose), a.formatter)
