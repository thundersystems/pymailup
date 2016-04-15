Client configuration
====================

A client instance use a configuration dict where you can configure *endpoints*, *credential*, *pagination* and *timeout*::

    _initial_client_configuration = {
        'MAILUP_END_POINTS': {
            'LOGON_END_POINT': 'https://services.mailup.com/Authorization/OAuth/LogOn',
            'AUTHORIZATION_END_POINT': 'https://services.mailup.com/Authorization/OAuth/Authorization',
            'TOKEN_END_POINT': 'https://services.mailup.com/Authorization/OAuth/Token',
            'CONSOLE_END_POINT': 'https://services.mailup.com/API/v1.1/Rest/ConsoleService.svc',
            'MAIL_STATISTICS_END_POINT': 'https://services.mailup.com/API/v1.1/Rest/MailStatisticsService.svc',
            'SEND_MESSAGE_END_POINT': 'https://send.mailup.com/API/v2.0/messages/sendmessage',
        },
        'MAILUP_CLIENT_ID': None,
        'MAILUP_CLIENT_SECRET': None,
        'MAILUP_USERNAME': None,
        'MAILUP_PASSWORD': None,
        'MAILUP_CLIENT_ATTEMPTS': 20,
        'MAILUP_DEFAULT_PAGE_SIZE': 50,
        'MAILUP_CLIENT_TIMEOUT': 30,
        'MAILUP_CLIENT_TIMEOUT_403': 60,
        'MAILUP_CLIENT_ATTEMPT_WAIT': 2,
    }

Through *client* instance you can access to dictionary with *configuration_dict* attribute.
For example, to change pagination of MailUp json response::

    mailup_client.configuration_dict['MAILUP_DEFAULT_PAGE_SIZE'] = 100



