""""""


import imp
import logging
import os
import sys
from website.settings import settings


logger = logging.getLogger("website.plugins")


_plugins = []


_hooks = {}


def load_plugins():
    """Load all plugins from ./_plugins"""
    plugin_dir = os.path.join(settings.__BASE, "_plugins")
    if not os.path.isdir(plugin_dir):
        return False
    else:
        possible_plugins = [name for name in os.listdir(plugin_dir)
                            if os.path.isdir(os.path.join(plugin_dir, name))]
        for name in possible_plugins:
            try:
                fp, pathname, description = imp.find_module(name, [plugin_dir])
                plugin = imp.load_module(name, fp, pathname, description)
            except ImportError:
                logger.warning("The plugin _plugins/%s cannot be loaded" % name)
            else:
                logger.info("Load plugin _plugins/%s" % name)
                _plugins.append(plugin)
            finally:
                if fp:
                    fp.close()
    return len(_plugins) > 0


def register_hook(name, func):
    """Register a function to a specific hook"""
    if name not in _hooks:
        _hooks[name] = []
    _hooks[name].append(func)


def fire_hook(name, **kwargs):
    """Fire a hook, accept keyword args and pass them on"""
    if name in _hooks:
        for hook in _hooks[name]:
            hook(**kwargs)
    return True

