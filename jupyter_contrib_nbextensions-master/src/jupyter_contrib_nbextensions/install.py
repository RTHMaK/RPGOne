# -*- coding: utf-8 -*-
"""API to install/remove all jupyter_contrib_nbextensions."""

from __future__ import (
    absolute_import, division, print_function, unicode_literals,
)

import errno
import os

import jupyter_highlight_selected_word
import latex_envs
import psutil
from jupyter_contrib_core.notebook_compat import nbextensions
from jupyter_nbextensions_configurator.application import (
    EnableJupyterNbextensionsConfiguratorApp,
)
from traitlets.config import Config
from traitlets.config.manager import BaseJSONConfigManager

import jupyter_contrib_nbextensions.nbconvert_support


class NotebookRunningError(Exception):
    pass


def notebook_is_running():
    """Return true if a notebook process appears to be running."""
    for p in psutil.process_iter():
        # p.name() can throw exceptions due to zombie processes on Mac OS X, so
        # ignore psutil.ZombieProcess
        # (See https://code.google.com/p/psutil/issues/detail?id=428)

        # It isn't enough to search just the process name, we have to
        # search the process command to see if jupyter-notebook is running.

        # Checking the process command can cause an AccessDenied exception to
        # be thrown for system owned processes, ignore those as well
        try:
            # use lower, since python may be Python, e.g. on OSX
            if ('python' or 'jupyter') in p.name().lower():
                for arg in p.cmdline():
                    # the missing k is deliberate!
                    # The usual string 'jupyter-notebook' can get truncated.
                    if 'jupyter-noteboo' in arg:
                        return True
        except (psutil.ZombieProcess, psutil.AccessDenied):
            pass
        return False


def toggle_install(install, user=False, sys_prefix=False, overwrite=False,
                   symlink=False, prefix=None, nbextensions_dir=None,
                   logger=None):
    """Install or remove all jupyter_contrib_nbextensions files & config."""
    if notebook_is_running():
        raise NotebookRunningError(
            'Cannot configure while the Jupyter notebook server is running')
    _check_conflicting_kwargs(user=user, sys_prefix=sys_prefix, prefix=prefix,
                              nbextensions_dir=nbextensions_dir)
    toggle_install_files(
        install, user=user, sys_prefix=sys_prefix, overwrite=overwrite,
        symlink=symlink, prefix=prefix, nbextensions_dir=nbextensions_dir,
        logger=logger)
    toggle_install_config(
        install, user=user, sys_prefix=sys_prefix, logger=logger)


def toggle_install_files(install, user=False, sys_prefix=False, logger=None,
                         overwrite=False, symlink=False, prefix=None,
                         nbextensions_dir=None):
    """Install/remove jupyter_contrib_nbextensions files."""
    if notebook_is_running():
        raise NotebookRunningError(
            'Cannot configure while the Jupyter notebook server is running')
    kwargs = dict(user=user, sys_prefix=sys_prefix, prefix=prefix,
                  nbextensions_dir=nbextensions_dir)
    _check_conflicting_kwargs(**kwargs)
    kwargs['logger'] = logger
    if logger:
        logger.info(
            '{} jupyter_contrib_nbextensions nbextension files {} {}'.format(
                'Installing' if install else 'Uninstalling',
                'to' if install else 'from',
                'jupyter data directory'))
    component_nbext_packages = [
        jupyter_contrib_nbextensions,
        jupyter_highlight_selected_word,
        latex_envs,
    ]
    for mod in component_nbext_packages:
        if install:
            nbextensions.install_nbextension_python(
                mod.__name__, overwrite=overwrite, symlink=symlink, **kwargs)
        else:
            nbextensions.uninstall_nbextension_python(mod.__name__, **kwargs)


def toggle_install_config(install, user=False, sys_prefix=False, logger=None):
    """Install/remove contrib nbextensions to/from jupyter_nbconvert_config."""
    if notebook_is_running():
        raise NotebookRunningError(
            'Cannot configure while the Jupyter notebook server is running')
    _check_conflicting_kwargs(user=user, sys_prefix=sys_prefix)
    config_dir = nbextensions._get_config_dir(user=user, sys_prefix=sys_prefix)
    if logger:
        logger.info(
            '{} jupyter_contrib_nbextensions items {} config in {}'.format(
                'Installing' if install else 'Uninstalling',
                'to' if install else 'from',
                config_dir))

    # Configure the jupyter_nbextensions_configurator serverextension to load
    if install:
        configurator_app = EnableJupyterNbextensionsConfiguratorApp(
            user=user, sys_prefix=sys_prefix, logger=logger)
        configurator_app.start()
        nbextensions.enable_nbextension(
            'notebook', 'contrib_nbextensions_help_item/main',
            user=user, sys_prefix=sys_prefix, logger=logger)
    else:
        nbconf_cm = BaseJSONConfigManager(
            config_dir=os.path.join(config_dir, 'nbconfig'))
        for require, section in {
                'contrib_nbextensions_help_item/main': 'notebook'}.items():
            if logger:
                logger.info('- Disabling {}'.format(require))
                logger.info(
                    '--  Editing config: {}'.format(
                        nbconf_cm.file_name(section)))
        # disabled_conf['load_extensions'][require] = None
        nbconf_cm.update('notebook', {'load_extensions': {require: None}})

    # Set extra template path, pre- and post-processors for nbconvert
    cm = BaseJSONConfigManager(config_dir=config_dir)
    config_basename = 'jupyter_nbconvert_config'
    config = cm.get(config_basename)
    # avoid warnings about unset version
    config.setdefault('version', 1)
    if logger:
        logger.info(
            u'- Editing config: {}'.format(cm.file_name(config_basename)))

    # Set extra template path, pre- and post-processors for nbconvert
    if logger:
        logger.info('--  Configuring nbconvert template path')
    # our templates directory
    _update_config_list(config, 'Exporter.template_path', [
        '.',
        jupyter_contrib_nbextensions.nbconvert_support.templates_directory(),
    ], install)
    # our preprocessors
    if logger:
        logger.info('--  Configuring nbconvert preprocessors')
    proc_mod = 'jupyter_contrib_nbextensions.nbconvert_support'
    _update_config_list(config, 'Exporter.preprocessors', [
        proc_mod + '.CodeFoldingPreprocessor',
        proc_mod + '.PyMarkdownPreprocessor',
    ], install)
    if logger:
        logger.info(
            u'- Writing config: {}'.format(cm.file_name(config_basename)))
    _set_managed_config(cm, config_basename, config, logger=logger)


def install(user=False, sys_prefix=False, prefix=None, nbextensions_dir=None,
            logger=None, overwrite=False, symlink=False):
    """Install all jupyter_contrib_nbextensions files & config."""
    return toggle_install(
        True, user=user, sys_prefix=sys_prefix, prefix=prefix,
        nbextensions_dir=nbextensions_dir, logger=logger,
        overwrite=overwrite, symlink=symlink)


def uninstall(user=False, sys_prefix=False, prefix=None, nbextensions_dir=None,
              logger=None):
    """Uninstall all jupyter_contrib_nbextensions files & config."""
    return toggle_install(
        False, user=user, sys_prefix=sys_prefix, prefix=prefix,
        nbextensions_dir=nbextensions_dir, logger=logger)

# -----------------------------------------------------------------------------
# Private API
# -----------------------------------------------------------------------------


def _check_conflicting_kwargs(**kwargs):
    if sum(map(bool, kwargs.values())) > 1:
        raise nbextensions.ArgumentConflict(
            "Cannot specify more than one of {}.\nBut recieved {}".format(
                ', '.join(kwargs.keys),
                ', '.join(['{}={}'.format(k, v)
                           for k, v in kwargs.items() if v])))


def _set_managed_config(cm, config_basename, config, logger=None):
    """Write config owned by the given config manager, removing if empty."""
    config_path = cm.file_name(config_basename)
    msg = 'config file {}'.format(config_path)
    if len(config) > ('version' in config):
        if logger:
            logger.info('--  Writing updated {}'.format(msg))
        # use set to ensure removed keys get removed
        cm.set(config_basename, config)
    else:
        if logger:
            logger.info('--  Removing now-empty {}'.format(msg))
        try:
            os.remove(config_path)
        except OSError as ex:
            if ex.errno != errno.ENOENT:
                raise


def _update_config_list(config, list_key, values, insert):
    """
    Add or remove items as required to/from a config value which is a list.

    This exists in order to avoid clobbering values other than those which we
    wish to add/remove, and to neatly remove a list when it ends up empty.
    """
    section, list_key = list_key.split('.')
    conf_list = config.setdefault(section, Config()).setdefault(list_key, [])
    list_alteration_method = 'append' if insert else 'remove'
    for val in values:
        if (val in conf_list) != insert:
            getattr(conf_list, list_alteration_method)(val)
    if not insert:
        # remove empty list
        if len(conf_list) == 0:
            config[section].pop(list_key)
        # remove empty section
        if len(config[section]) == 0:
            config.pop(section)
