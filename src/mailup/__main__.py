"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -m mailup` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``mailup.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``mailup.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""

import datetime
import getopt
import random
import sys
import string
import time
import unittest

from mailup import exceptions

# LOGGER
from mailup.logger import LoggerSingleton
ls = LoggerSingleton()
# ls.info('Logger work!')

# MAILUP CONFIGURATION
client_id = None
client_secret = None
username = None
password = None
owner_email = None
log_level = None
logger_enabled = False

log_level_dict = {
    'CRITICAL': 50,
    'ERROR': 40,
    'WARNING': 30,
    'INFO': 20,
    'DEBUG': 10,
    'NOTSET': 0,
}


class TestPymailupBase(unittest.TestCase):

    def __init__(self, methodName='runTest'):
        # TEST LIST SETTINGS
        self.test_list_name = 'TEST-PYMAILUP'

        # TEST GROUP SETTINGS
        self.test_group_name = 'TEST-PYMAILUP-GROUP'

        # CLIENT AND PROVIDER
        from mailup.providers import MailUpComponentProvider
        from mailup.clients import MailUpClientSingleton
        self.client = MailUpClientSingleton(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
        )
        self.client.configuration_dict['MAILUP_DEFAULT_PAGE_SIZE'] = 5
        self.provider = MailUpComponentProvider(client=self.client)

        # SETTING LOG
        from mailup.logger import LoggerSingleton
        logger_singleton = LoggerSingleton()
        logger_singleton.setLevel(log_level)
        if logger_enabled:
            logger_singleton.disabled = False
        else:
            logger_singleton.disabled = True
        super(TestPymailupBase, self).__init__(methodName)

    # UTILS
    def get_or_create_test_list(self):

        lists = self.provider.filter_lists(filters={'Name': self.test_list_name})
        if lists:
            test_list = lists[0]
        else:
            # IF TEST LIST NOT EXISTS, ITS CREATED
            data_dict = {
                'Name': self.test_list_name,
                'replyto': owner_email,
                'owneremail': owner_email
            }
            test_list = self.provider.create_list(data_dict)
            while not test_list:
                lists = self.provider.filter_lists(filters={'Name': self.test_list_name})
                test_list = lists[0]

        return test_list

    def get_or_create_test_group(self):
        test_list = self.get_or_create_test_list()
        test_group = None
        while not test_group:
            groups = self.provider.filter_groups(list_id=test_list.id, filters={'Name': self.test_group_name})

            # IF TEST GROUP NOT EXISTS, ITS CREATED
            if groups:
                test_group = groups[0]
            else:
                data_dict = {
                    'Name': self.test_group_name,
                    'idList': test_list.id,
                    'Notes': 'group generating with pymailup test'
                }
                test_group = self.provider.create_group(data_dict)
        return test_group

    def get_random_email_string(self):
        return '{}@yopmail.it'.format(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))

    def get_random_name_string(self):
        first = ''.join(random.choice(string.lowercase) for i in range(7))
        last = ''.join(random.choice(string.lowercase) for i in range(7))
        return '{} {}'.format(first.title(), last.title())

    def create_random_recipient(self):
        from components import Recipient

        test_list = self.get_or_create_test_list()

        random_email = self.get_random_email_string()
        random_name = self.get_random_name_string()
        data_dict = {
            'Name': random_name,
            'Email': random_email,
            'idList': test_list.id
        }
        return Recipient(data_dict, client=self.client)

    def create_random_recipient_list(self, recipient_count=None):
        if not recipient_count:
            recipient_count = random.randint(2, 5)
        recipients_list = []
        for i in range(recipient_count):
            recipients_list.append(self.create_random_recipient())
            time.sleep(0.5)
        return recipients_list

    def create_random_message(self):
        test_list = self.get_or_create_test_list()
        return self.provider.create_message(
            {
                'idList': test_list.id,
                'Subject': 'PyMailUp Test Email',
                'Content': '',
                'Embed': False,
                'IsConfirmation': False ,
                'Notes': 'Message create for test of pymailup library',
                'Tags': [],
                'TrackingInfo': {
                    'CustomParams': '',
                    'Enabled': True,
                    'Protocols': ['http:', 'ftp:', 'news:']
                }

            }
        )


class TestClient(TestPymailupBase):

    def test_pagination_exact(self):
        pagination = self.provider.client.configuration_dict['MAILUP_DEFAULT_PAGE_SIZE']
        test_list = self.get_or_create_test_list()
        test_list.unsubscribe_recipients_list(test_list.get_subscribers(), wait_import=True)
        test_recipient_list = self.create_random_recipient_list(recipient_count=pagination*4)
        test_list.subscribe_recipients_list(test_recipient_list, wait_import=True)
        assert len(test_list.get_subscribers()) == len(test_recipient_list)

    def test_pagination_not_exact(self):
        pagination = self.provider.client.configuration_dict['MAILUP_DEFAULT_PAGE_SIZE']
        test_list = self.get_or_create_test_list()
        test_list.unsubscribe_recipients_list(test_list.get_subscribers(), wait_import=True)
        test_recipient_list = self.create_random_recipient_list(recipient_count=pagination*4+1)
        test_list.subscribe_recipients_list(test_recipient_list, wait_import=True)
        assert len(test_list.get_subscribers()) == len(test_recipient_list)


class TestList(TestPymailupBase):

    # # BASE
    # def test_get_or_create(self):
    #     test_list = self.get_or_create_test_list()
    #     assert test_list.name == self.test_list_name
    #
    # # PROVIDER
    # def test_get(self):
    #     test_list = self.get_or_create_test_list()
    #     list_id = test_list.id
    #     provided_list = self.provider.get_list(list_id)
    #     assert provided_list.id == test_list.id
    #
    # def test_all(self):
    #     self.get_or_create_test_list()
    #     lists_list = self.provider.all_lists()
    #     assert len(lists_list) > 0
    #
    # def test_filter(self):
    #     test_list = self.get_or_create_test_list()
    #     list_name = test_list.name
    #     provided_lists = self.provider.filter_lists(filters={'Name': list_name})
    #     assert provided_lists[0].name == test_list.name
    #
    # # COMPONENT METHODS
    # def test_save(self):
    #     test_list = self.get_or_create_test_list()
    #     test_list.name = self.test_list_name
    #     saved = test_list.save()
    #     assert saved is not None
    #
    # def test_get_groups(self):
    #     test_list = self.get_or_create_test_list()
    #     self.get_or_create_test_group()
    #     groups = test_list.get_groups()
    #     assert len(groups) > 0

    def test_get_recipients(self):
        test_list = self.get_or_create_test_list()
        recipients_count = len(test_list.get_recipients())

        test_recipients_list = self.create_random_recipient_list()
        test_list.subscribe_recipients_list(test_recipients_list, wait_import=True)

        assert len(test_list.get_recipients()) == recipients_count + len(test_recipients_list)

    def test_get_subscribers(self):
        test_list = self.get_or_create_test_list()
        subscribers_count = len(test_list.get_subscribers())

        test_recipients_list = self.create_random_recipient_list()
        test_list.subscribe_recipients_list_forced(test_recipients_list, wait_import=True)

        assert len(test_list.get_subscribers()) == subscribers_count + len(test_recipients_list)

    def test_get_unsubscribers(self):
        test_list = self.get_or_create_test_list()
        unsubscribers_count = len(test_list.get_unsubscribers())

        test_recipients_list = self.create_random_recipient_list()
        test_list.unsubscribe_recipients_list(test_recipients_list, wait_import=True)

        assert len(test_list.get_unsubscribers()) == unsubscribers_count + len(test_recipients_list)

    def test_get_pending(self):
        test_list = self.get_or_create_test_list()
        pending_count = len(test_list.get_pending())

        test_recipients_list = self.create_random_recipient_list()
        test_list.subscribe_recipients_list_forced(test_recipients_list, confirm_email=True, wait_import=True)

        assert len(test_list.get_pending()) == pending_count + len(test_recipients_list)

    def test_subscribe_recipients_list(self):
        test_list = self.get_or_create_test_list()
        subscribers_count = len(test_list.get_subscribers())

        test_recipients_list = self.create_random_recipient_list()
        test_list.subscribe_recipients_list(test_recipients_list, wait_import=True)

        assert len(test_list.get_subscribers()) == subscribers_count + len(test_recipients_list)

    def test_subscribe_recipients_list_forced(self):
        test_list = self.get_or_create_test_list()

        test_recipients_list = self.create_random_recipient_list()
        test_list.unsubscribe_recipients_list(test_recipients_list, wait_import=True)

        unsubscribers = test_list.get_unsubscribers()
        test_list.subscribe_recipients_list_forced(unsubscribers, wait_import=True)

        assert len(test_list.get_unsubscribers()) == 0

    def test_unsubscribe_recipients_list(self):
        test_list = self.get_or_create_test_list()

        test_recipients_list = self.create_random_recipient_list()
        test_list.subscribe_recipients_list(test_recipients_list, wait_import=True)

        subscribers = test_list.get_subscribers()
        test_list.unsubscribe_recipients_list(subscribers, wait_import=True)
        assert len(test_list.get_subscribers()) == 0

    # def test_send_confirmation_email(self):
    #     test_list = self.get_or_create_test_list()
    #     test_recipients_list = self.create_random_recipient_list()
    #
    #     import_id = test_list.subscribe_recipients_list(test_recipients_list, confirm_email=True)
    #     test_list.send_confirmation_email(import_id)
    #     pass  # todo: assert


class TestGroup(TestPymailupBase):

    # BASE
    def test_get_or_create(self):
        test_group = self.get_or_create_test_group()
        assert test_group.name == self.test_group_name

    # COMPONENT METHODS
    def test_save(self):
        test_group = self.get_or_create_test_group()
        test_group.name = self.test_group_name
        saved = test_group.save()
        assert saved is not None

    def test_delete(self):
        test_group = self.get_or_create_test_group()
        group_id = test_group.id
        list_id = test_group.list_id
        test_group.delete()
        try:
            self.provider.get_group(list_id, group_id)
        except exceptions.GroupNotFoundException:
            return True
        return False

    def test_get_subscribers(self):
        test_group = self.get_or_create_test_group()
        subscribers_count = len(test_group.get_subscribers())

        test_recipients_list = self.create_random_recipient_list()
        test_group.subscribe_recipients_list_forced(test_recipients_list, wait_import=True)

        assert len(test_group.get_subscribers()) == subscribers_count + len(test_recipients_list)

    def test_insert_recipient(self):
        test_list = self.get_or_create_test_list()
        test_group = self.get_or_create_test_group()

        random_recipient = self.create_random_recipient()
        test_list.subscribe_recipients_list([random_recipient])
        time.sleep(5)
        test_recipient = self.provider.get_recipient(test_list.id, email=random_recipient.email)

        subscribers_count = len(test_group.get_subscribers())
        test_group.insert_recipient(test_recipient.id)

        assert len(test_group.get_subscribers()) == subscribers_count + 1

    def test_extract_recipient(self):
        test_group = self.get_or_create_test_group()
        test_recipient = self.create_random_recipient()
        test_group.subscribe_recipients_list_forced([test_recipient], wait_import=True)

        group_subscribers = test_group.get_subscribers()
        group_subscribers_count = len(group_subscribers)

        recipient_to_remove = group_subscribers[0]

        test_group.extract_recipient(recipient_to_remove.id)
        assert len(test_group.get_subscribers()) == group_subscribers_count - 1


class TestRecipient(TestPymailupBase):

    # BASE
    def test_get_or_create(self):
        test_recipients_list = self.create_random_recipient_list(recipient_count=2)
        assert len(test_recipients_list) == 2

    # COMPONENT METHODS
    def test_save(self):
        recipient_instance = self.create_random_recipient()
        recipient = self.provider.create_recipient(recipient_instance.data_dict)
        saved = recipient.save()
        assert saved is not None

    def test_add_pending_to_list(self):
        test_list = self.get_or_create_test_list()
        pending_recipients = test_list.get_pending()

        recipient = self.create_random_recipient()
        recipient.add_to_list(test_list.id, confirm_email=True)
        assert len(test_list.get_pending()) == len(pending_recipients) + 1

    def test_add_subscriber_to_list(self):
        test_list = self.get_or_create_test_list()
        subscribers_recipients = test_list.get_subscribers()

        recipient = self.create_random_recipient()
        recipient.add_to_list(test_list.id, confirm_email=False)
        assert len(test_list.get_subscribers()) == len(subscribers_recipients) + 1

    def test_add_to_group(self):
        test_group = self.get_or_create_test_group()
        group_members = test_group.get_subscribers()

        test_list = self.get_or_create_test_list()
        recipient = self.create_random_recipient()

        test_list.subscribe_recipients_list([recipient])

        recipient.add_to_group(test_group.id)
        assert len(test_group.get_subscribers()) == len(group_members) + 1


class TestMessage(TestPymailupBase):

    # BASE
    def test_get_or_create(self):
        test_message = self.create_random_message()
        assert test_message

    # PROVIDER
    def test_get(self):
        test_message = self.create_random_message()

        test_message = self.provider.get_message(test_message.list_id, test_message.id)
        assert test_message

    def test_all(self):
        test_list = self.get_or_create_test_list()

        messages_list_count = len(self.provider.all_messages(test_list.id))
        self.create_random_message()
        assert len(self.provider.all_messages(test_list.id)) == messages_list_count + 1

    def test_filter(self):
        test_list = self.get_or_create_test_list()
        test_message = self.create_random_message()
        provided_messages = self.provider.filter_messages(list_id=test_list.id, filters=test_message.data_dict)
        assert len(provided_messages) == 1

    # COMPONENT METHODS
    def test_save(self):
        test_list = self.get_or_create_test_list()
        test_message = self.create_random_message()
        test_message.subject = 'CaSuAlStRiNg'
        test_message.save()
        provided_messages = self.provider.filter_messages(list_id=test_list.id, filters={'idMessage': test_message.id})
        assert len(provided_messages) == 1 and provided_messages[0].subject == 'CaSuAlStRiNg'

    def test_send_to_list(self):
        test_list = self.get_or_create_test_list()
        test_message = self.create_random_message()
        test_recipients_list = self.create_random_recipient_list(recipient_count=1)
        test_list.subscribe_recipients_list(test_recipients_list, wait_import=True)
        subscribers_count = len(test_list.get_subscribers())
        send_statistic = test_message.send_to_list(test_list.id)
        assert subscribers_count == send_statistic['Sent']

    def test_send_to_group(self):
        test_group = self.get_or_create_test_group()
        test_message = self.create_random_message()
        test_recipients_list = self.create_random_recipient_list(recipient_count=1)
        test_group.subscribe_recipients_list(test_recipients_list, wait_import=True)
        subscribers_count = len(test_group.get_subscribers())
        send_statistic = test_message.send_to_group(test_group.id)
        assert subscribers_count == send_statistic['Sent']

    def test_send_to_recipient(self):
        test_list = self.get_or_create_test_list()
        test_recipient = self.create_random_recipient()
        test_list.subscribe_recipients_list([test_recipient], wait_import=True)
        test_message = self.create_random_message()
        provided_recipient = self.provider.get_recipient(test_list.id, email=test_recipient.email)
        send_statistic = test_message.send_to_recipient(recipient_id=provided_recipient.id)
        assert send_statistic['Sent'] == 1

if __name__ == '__main__':

    opts, args = getopt.getopt(sys.argv[1:], '', [
        'client-id=',
        'client-secret=',
        'username=',
        'password=',
        'owner-email=',
        'log-level=',
        'logger-enabled',
    ])

    for option, value in opts:
        if option == '--client-id':
            client_id = value
        if option == '--client-secret':
            client_secret = value
        if option == '--username':
            username = value
        if option == '--password':
            password = value
        if option == '--owner-email':
            owner_email = value
        if option == '--logger-enabled':
            logger_enabled = True
        if option == '--log-level':
            logger_enabled = True
            if value in log_level_dict.keys():
                log_level = log_level_dict[value]
            if value in log_level_dict.values():
                log_level = value

    if not log_level:
        log_level = log_level_dict['INFO']

    if not client_id or not client_secret or not username or not password or not owner_email:
        ls.error('MailUp credential are required')
    else:
        del sys.argv[1:]
        unittest.main()
