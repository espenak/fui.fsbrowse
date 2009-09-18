===============================================================================
README
===============================================================================

Plone product which makes files from the file system available within plone.

    - http://pypi.python.org/pypi/fui.fsbrowse/
    - http://github.com/espenak/fui.fsbrowse/


Install
-------

You can install this product in Plone using buildout.

    1. Add ``fui.fsbrowse`` to ``buildout.cfg``::

        [buildout]
        ...
        eggs =
            ...
            fui.fsbrowse

        [instance]
        ...
        zcml = 
            ...
            fui.fsbrowse

    2. Run (maybe backup first..)::

        ~$ buildout -N

    3. Install the plugin using *Site Setup* in your Plone site.




For developers
--------------

Release a new version to pypi.python.org with::

    ~$ python setup.py egg_info -RDb "" sdist upload
