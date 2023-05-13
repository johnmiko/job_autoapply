# from os.path import dirname, basename, isfile, join
# import glob
# modules = glob.glob(join(dirname(__file__), "*.py"))
# __all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
# print(modules)
# __all__.remove("b")
# print("heer")
# print(__all__)
#
# #This file is needed so this directory can be imported as a package
#
#
# # __all__ = ["a"]
#
# #This finds all of the files in this directory that do not start with '__'  and adds them to the 'all' variable. This allows us to import all of the functions and classes inside each module of the package by writing 'from ht import *'
#
# ##List of all modules in this package
# # __all__ = []
# #
# # import pkgutil
# # import inspect
# #
# # for loader, name, is_pkg in pkgutil.walk_packages(__path__):
# #     ##Iterator to loop through all modules
# #     module = loader.find_module(name).load_module(name)
# #
# #     for name, value in inspect.getmembers(module):
# #         if name.startswith('__'):
# #             continue
# #
# #         globals()[name] = value
# #         __all__.append(name)
