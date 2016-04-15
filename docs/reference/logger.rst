Logger
======

Default logger
++++++++++++++

Pymailup provide a preconfigured logger. If you do not perform any configuration it creates a logger disabled but set to level INFO.
Remember that the preconfigured logger is a standard python logger refer to the `python documentation <https://docs.python.org/2/library/logging.html>`_
to evaluate all available possibilities.

For example if you have a client configured and try to log::

    mailup_client.logger.info('info message')

nothing will be logged, bat if you enable the logger before::

    mailup_client.logger.disabled = False
    mailup_client.logger.info('info message')

a log is generated::

    2016-04-12 21:57:31,685 [INFO]: info message

In this situation DEBUG log are not generated. If you want see log in DEBUG level you must set logger to DEBUG level::

    import logging
    mailup_client.logger.setLevel(logging.DEBUG)
    mailup_client.logger.debug('debug message')


that will log::

    2016-04-12 22:04:25,022 [DEBUG]: debug message



Custom logger
+++++++++++++

If you need to use a custom logger, all you have to do is build it and assign it to the client (or objects where pymailup
provides a logger), for example::

    import logging
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger('my_logger')
    mailup_client.logger = logger

having the possibility to configure the logger to the desired level with the desired handler etc ..


Singleton logger
++++++++++++++++

While your logger is the default or custom, if you want that all loggers have a uniform behavior a singleton logger
is recommended::

    from mailup.logger import LoggerSingleton
    singleton_logger = LoggerSingleton(logger)
    mailup_client.logger = singleton_logger

