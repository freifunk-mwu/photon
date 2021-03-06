'''
.. |params_locations_dict| replace::
    If `locations` is not a list, but a dictionary,
    all values in the dictionary will be used
    (as specified in :func:`util.structures.to_list`)
.. |param_locations_none| replace::
    If `locations` is set to ``None`` (by default),
    it will be filled with the output of :func:`get_locations`.
'''

from os import environ as _environ
from os import listdir as _listdir
from os import makedirs as _makedirs
from os import path as _path
from os import remove as _remove
from os import sep as _sep
from shutil import copy2 as _copy2
from shutil import rmtree as _rmtree
from sys import argv as _argv

from photon import IDENT


def get_locations():
    '''
    Compiles default locations

    :returns:
        A dictionary with folders as values:

    * 'home_dir': Your home-directory (:file:`~`)

    * 'call_dir': Where you called the first Python script from. (``argv[0]``)

    * 'conf_dir': The :envvar:`XDG_CONFIG_HOME`-directory + \
    ``photon`` (:file:`~/.config/photon`)

    * 'data_dir': The :envvar:`XDG_DATA_HOME`-directory + \
    ``photon`` (:file:`~/.local/share/photon`)

    .. note::

        * Both :func:`search_location` and :func:`make_locations` \
        have the argument `locations`.

        * |param_locations_none|
    '''

    home_dir = _path.expanduser('~')
    conf_dir = _path.join(
        _environ.get(
            'XDG_CONFIG_HOME',
            _path.join(home_dir, '.config')
        ),
        IDENT
    )
    data_dir = _path.join(
        _environ.get(
            'XDG_DATA_HOME',
            _path.join(home_dir, '.local', 'share')
        ),
        IDENT
    )

    return {
        'home_dir': home_dir,
        'call_dir': _path.dirname(_path.abspath(_argv[0])),
        'conf_dir': conf_dir,
        'data_dir': data_dir
    }


def make_locations(locations=None, verbose=True):
    '''
    Creates folders

    :param locations:
        A list of folders to create (can be a dictionary, see note below)
    :param verbose:
        Warn if any folders were created

    .. note::

        * |params_locations_dict|
        * |param_locations_none|
    '''

    from photon.util.structures import to_list
    from photon.util.system import shell_notify

    if not locations:
        locations = get_locations().values()
    locations = to_list(locations)

    r = list()
    for p in reversed(sorted(locations)):
        if not _path.exists(p):
            _makedirs(p)
            r.append(p)
    if verbose and r:
        shell_notify('path created', state=None, more=r)
    return r


def search_location(loc, locations=None,
                    critical=False, create_in=None, verbose=True):
    '''
    Locates files with a twist:

        * Check the existence of a file using the full path in `loc`

        * Search for the filename `loc` in `locations`

        * Create it's enclosing folders if the file does not exist. \
        use `create_in`

    :param loc:
        Filename to search
    :param locations:
        A list of possible locations to search within
        (can be a dictionary, see note below)
    :param critical:
        |appteardown| if file was not found
    :param create_in:
        If `loc` was not found, the folder `create_in` is created.
        If `locations` is a dictionary, `create_in` can also specify
        a key of `locations`. The value will be used then.
    :param verbose:
        Pass verbose flag to :func:`make_locations`
    :returns:
        The full path of `loc` in matched location

    .. note::
        * |params_locations_dict|

        * |param_locations_none|
    '''

    from photon.util.structures import to_list
    from photon.util.system import shell_notify

    if not locations:
        locations = get_locations()

    for p in reversed(sorted(to_list(locations))):
        f = _path.join(p, loc)
        if _path.exists(f):
            return f

    if _path.exists(_path.abspath(_path.expanduser(loc))):
        return _path.abspath(_path.expanduser(loc))

    if critical:
        shell_notify('could not locate', state=True, more=dict(
            file=loc, locations=locations
        ))

    if create_in:
        if isinstance(locations, dict):
            create_in = locations.get(create_in, create_in)
        make_locations(locations=[create_in], verbose=verbose)
        return _path.join(create_in, loc)


def change_location(src, tgt, move=False, verbose=True):
    '''
    Copies/moves/deletes locations

    :param src:
        Source location where to copy from
    :param tgt:
        Target location where to copy to

        * To backup `src`, set `tgt` explicitly to ``True``. \
        `tgt` will be set to `src` + '_backup_' + \
        :func:`util.system.get_timestamp` then

    :param move:
        Deletes original location after copy (a.k.a. move)

        * To delete `src` , set `tgt` explicitly to ``False`` \
        and `move` to ``True`` (be careful!!1!)

    :param verbose:
        Show warnings
    '''

    from photon.util.system import shell_notify

    if _path.exists(src):
        if tgt:
            if _path.isfile(src):
                _copy2(src, search_location(
                    tgt, create_in=_path.dirname(tgt), verbose=verbose)
                )
            else:
                for l in _listdir(src):
                    change_location(
                        _path.abspath(_path.join(src, l)),
                        _path.abspath(_path.join(tgt, l))
                    )
        if move:
            if _path.isdir(src) and not _path.islink(src):
                _rmtree(src)
            else:
                _remove(src)
        if verbose:
            shell_notify(
                '%s location' % (
                    'deleted'
                    if not tgt and move else
                    'moved'
                    if move else
                    'copied'
                ),
                more=dict(src=src, tgt=tgt)
            )


def backup_location(src, loc=None):
    '''
    Writes Backups of locations

    :param src:
        The source file/folder to backup
    :param loc:
        The target folder to backup into

        The backup will be called `src` + :func:`util.system.get_timestamp`.
        * If `loc` left to none, the backup gets written in the same \
        folder like `src` resides in

        * Otherwise the specified path will be used.
    '''

    from photon.util.system import get_timestamp

    src = _path.realpath(src)
    if not loc or not loc.startswith(_sep):
        loc = _path.dirname(src)

    pth = _path.join(_path.basename(src), _path.realpath(loc))
    out = '%s_backup_%s' % (_path.basename(src), get_timestamp())

    change_location(src, search_location(out, create_in=pth))
