# coding: utf-8 -*-

import ast
import time

from mailup import exceptions
from mailup.logger import LoggerSingleton
from mailup.utils import filter_dict


# DECORATOR
def client_enabled(function):

    def wrapper(*args, **kwargs):

        from clients import MailUpClient

        for arg in args:
            if hasattr(arg, 'client'):
                if not isinstance(getattr(arg, 'client'), MailUpClient):
                    raise exceptions.ClientNotEnabledException('MailUp client not instanced')
                if not arg.client.access_token:
                    raise exceptions.ClientNotEnabledException('MailUp client without access token')
        return function(*args, **kwargs)

    return wrapper


# COMPONENTS
class MailUpComponent(object):

    # MAILUP CLIENT SINGLETON
    client = None

    # LOGGER SINGLETON
    logger = None

    data_dict = None
    mailup_pattern_fields = dict()
    required_fields = list()

    # STATIC METHOD
    @staticmethod
    def check_data_dict(component, data_dict):
        missing_parameters = dict()
        for field in component.required_fields:
            if field not in data_dict:
                missing_parameters[field] = None
        if missing_parameters:
            raise exceptions.InvalidConfigurationException(missing_parameters)

    def __init__(self, data_dict, client=None, logger=None, **kwargs):
        self.client = client
        self.logger = logger or LoggerSingleton()

        if 'mailup_pattern_fields' in kwargs:
            self.mailup_pattern_fields = kwargs['mailup_pattern_fields']
        if 'required_fields' in kwargs:
            self.required_fields = kwargs['required_fields']

        # check data_dict integrity
        MailUpComponent.check_data_dict(self, data_dict)

        # Init Attribute
        self.data_dict = filter_dict(data_dict, self.mailup_pattern_fields)

        super(MailUpComponent, self).__init__()

    def __getattr__(self, name):
        field_pattern_dict = self.mailup_pattern_fields

        if name in self.mailup_pattern_fields.values():
            data_dict = object.__getattribute__(self, 'data_dict')

            # key that has "name" like value
            key = field_pattern_dict.keys()[field_pattern_dict.values().index(name)]
            return data_dict[key]
        else:
            return super(MailUpComponent, self).__getattribute__(name)

    def __setattr__(self, name, value):
        field_pattern_dict = self.mailup_pattern_fields

        if not name == 'data_dict':
            try:
                data_dict = object.__getattribute__(self, 'data_dict')
                if data_dict and name in field_pattern_dict.values():
                    # key that has "name" like value
                    key = field_pattern_dict.keys()[field_pattern_dict.values().index(name)]
                    if key in data_dict:
                        # data dict is updated
                        data_dict[key] = value
            except AttributeError:
                # super is invoked
                pass
        else:
            for property_name, property_value in value.iteritems():
                if property_name in field_pattern_dict.keys():
                    setattr(self, field_pattern_dict[property_name], property_value)

        return super(MailUpComponent, self).__setattr__(name, value)

    # COMMON METHODS
    @client_enabled
    def get_list(self):
        list_id = self.list_id

        from mailup.providers import MailUpComponentProvider

        provider = MailUpComponentProvider(
            client=self.client,
            logger=self.logger,
        )

        return provider.get_list(list_id=list_id)

    # COMMON ABSTRACT PROPERTY
    @property
    def id(self):
        raise NotImplementedError

    @id.setter
    def id(self, value):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError


class List(MailUpComponent):

    mailup_pattern_fields = {
        'Name': 'name',
        'idList': 'list_id',
        'idImport': 'import_id',
        'replyto': 'reply_to',
        'owneremail': 'owner_mail',
    }

    required_fields = ['Name']

    def __repr__(self):
        return u'<{class_name}: {list_name}>'.format(
            class_name=self.__class__.__name__,
            list_name=self.name,
        )

    # METHODS
    @client_enabled
    def save(self):
        if not self.id:
            self.logger.warning('List {list} has no id, a new list will be created'.format(list=self))

            from mailup.providers import MailUpComponentProvider

            provider = MailUpComponentProvider(
                client=self.client,
                logger=self.logger,
            )
            new_list = provider.create_list(data_dict=self.data_dict)

            self.data_dict = new_list.data_dict
            return self

        # MailUp BUG FIX: Only in this case MailUp use "IdList" and not "idList"
        data_dict = self.data_dict.copy()
        list_id = data_dict.pop('idList')
        data_dict['IdList'] = list_id

        # MailUp BUG FIX: Only if list is just created, save return null for few seconds
        saved_data_dict = None
        while not saved_data_dict:
            saved_data_dict = self.client.update_list(data_dict=data_dict)
            if not saved_data_dict:
                self.logger.warning('MailUp as returned None, repeating save..')

        # data_dict as more keys than saved_data_dict
        saved_data_dict = filter_dict(saved_data_dict, self.mailup_pattern_fields)
        self.data_dict.update(saved_data_dict)

        self.logger.info('List {list_id} has been successfully saved'.format(list_id=self.id))
        return self

    @client_enabled
    def get_groups(self):
        from mailup.providers import MailUpComponentProvider

        provider = MailUpComponentProvider(
            client=self.client,
            logger=self.logger,
        )

        group_list = provider.all_groups(
            list_id=self.id
        )
        return group_list

    @client_enabled
    def get_recipients(self, status=None):

        from mailup.providers import MailUpComponentProvider

        provider = MailUpComponentProvider(
            client=self.client,
            logger=self.logger,
        )

        if not status:
            return provider.all_recipients(
                list_id=self.id,
            )
        else:
            if status == 'subscribed':
                return provider.all_recipients_subscribed(
                    list_id=self.id,
                )
            if status == 'unsubscribed':
                return provider.all_recipients_unsubscribed(
                    list_id=self.id,
                )
            if status == 'pending':
                return provider.all_recipients_pending(
                    list_id=self.id,
                )

    @client_enabled
    def get_subscribers(self):
        from mailup.providers import MailUpComponentProvider

        provider = MailUpComponentProvider(
            client=self.client,
            logger=self.logger,
        )

        return provider.all_recipients_subscribed(
            list_id=self.id,
        )

    @client_enabled
    def get_unsubscribers(self):
        from mailup.providers import MailUpComponentProvider

        provider = MailUpComponentProvider(
            client=self.client,
            logger=self.logger,
        )

        return provider.all_recipients_unsubscribed(
            list_id=self.id,
        )

    @client_enabled
    def get_pending(self):
        from mailup.providers import MailUpComponentProvider

        provider = MailUpComponentProvider(
            client=self.client,
            logger=self.logger,
        )

        return provider.all_recipients_pending(
            list_id=self.id,
        )

    @client_enabled
    def subscribe_recipients_list(self, recipients, confirm_email=False, wait_import=False):
        list_recipient_data_dict = []
        for recipient in recipients:
            list_recipient_data_dict.append(recipient.data_dict)

        import_id = self.client.subscribe_recipients_to_list(
            list_id=self.id,
            list_data_dict=list_recipient_data_dict,
            confirm_email=confirm_email,  # confirm_email=True => "Pending"; confirm_email=False => "Subscribed"
        )
        self.logger.info(
            'Subscribe in list {list_id} request submitted to MailUp, import_id={import_id}'.format(
                list_id=self.id,
                import_id=import_id,
            )
        )
        if wait_import:
            # WAITING IMPORT IS COMPLETE
            import_complete = False
            while not import_complete:
                status = self.client.read_import_status(import_id)
                self.logger.warning('Waiting 2 seconds import is complete..')
                time.sleep(2)
                import_complete = status['Completed']
        return import_id

    @client_enabled
    def subscribe_recipients_list_forced(self, recipients, confirm_email=False, wait_import=False):
        list_recipient_data_dict = []
        for recipient in recipients:
            list_recipient_data_dict.append(recipient.data_dict)

        import_id = self.client.subscribe_recipients_to_list(
            list_id=self.id,
            list_data_dict=list_recipient_data_dict,
            confirm_email=confirm_email,  # confirm_email=True => "Pending"; confirm_email=False => "Subscribed"
            import_type="asOptin",
        )
        self.logger.info(
            'Recipients are been subscribed with import_id={import_id} in list {list_id}'.format(
                list_id=self.id,
                import_id=import_id,
            )
        )
        if wait_import:
            # WAITING IMPORT IS COMPLETE
            import_complete = False
            while not import_complete:
                status = self.client.read_import_status(import_id)
                self.logger.warning('Waiting 2 seconds import is complete..')
                time.sleep(2)
                import_complete = status['Completed']
        return import_id

    @client_enabled
    def unsubscribe_recipients_list(self, recipients, wait_import=False):
        list_recipient_data_dict = []
        for recipient in recipients:
            list_recipient_data_dict.append(recipient.data_dict)

        import_id = self.client.unsubscribe_recipients_to_list(
            list_id=self.id,
            list_data_dict=list_recipient_data_dict,
            import_type='asOptout',  # import_type=asOptout: if specified, the given recipients' status is set to "unsubscribe",
        )
        self.logger.info(
            'Recipients are been unsubscribed with import_id={import_id} in list {list_id}'.format(
                list_id=self.id,
                import_id=import_id,
            )
        )
        if wait_import:
            # WAITING IMPORT IS COMPLETE
            import_complete = False
            while not import_complete:
                status = self.client.read_import_status(import_id)
                self.logger.warning('Waiting 2 seconds import is complete..')
                time.sleep(2)
                import_complete = status['Completed']
        return import_id

    @client_enabled
    def send_confirmation_email(self, import_id, send_date=None):
        response = self.client.prepare_to_send_import(import_id)
        sending_info = ast.literal_eval(str(response))
        sending_id = sending_info['idSending']

        # send_import_sending return other sending info
        other_sending_info = self.client.send_import_sending(
            sending_id=sending_id,
            send_date=send_date
        )
        self.logger.info(
            'Confirmation emails are been sent (sending_id={sending_id}) to import {import_id}'.format(
                sending_id=sending_id,
                import_id=import_id,
            )
        )
        return other_sending_info

    def get_import_status(self, import_id):
        return self.client.read_import_status(import_id)

    # PROPERTY
    @property
    def id(self):
        try:
            return self.data_dict['idList']
        except KeyError:
            return None

    @id.setter
    def id(self, value):
        self.data_dict['idList'] = value


class Group(MailUpComponent):

    mailup_pattern_fields = {
        'Deletable': 'deletable',
        'Name': 'name',
        'Notes': 'note',
        'idGroup': 'group_id',
        'idList': 'list_id',
        'idImport': 'import_id'
    }

    required_fields = ['Name', 'idList', 'Notes']

    def __repr__(self):
        return u'<{class_name}: {group_name}>'.format(
            class_name=self.__class__.__name__,
            group_name=self.name,
        )

    # METHODS
    @client_enabled
    def save(self):
        if not self.id:
            self.logger.warning('Group {group} has no id, a new group will be created'.format(group=self))

            from mailup.providers import MailUpComponentProvider

            provider = MailUpComponentProvider(
                client=self.client,
                logger=self.logger,
            )

            new_group = provider.create_group(
                data_dict=self.data_dict,
            )
            self.data_dict = new_group.data_dict
            return self

        saved_data_dict = self.client.update_group(
            list_id=self.list_id,
            group_id=self.id,
            data_dict=self.data_dict
        )
        saved_data_dict = filter_dict(saved_data_dict, self.mailup_pattern_fields)
        self.data_dict.update(saved_data_dict)
        self.logger.info('Group {group_id} has been successfully saved'.format(group_id=self.id))
        return self

    @client_enabled
    def delete(self):
        self.client.delete_group(
            list_id=self.list_id,
            group_id=self.id
        )
        self.logger.info('Group with id {group_id} has been deleted')

    @client_enabled
    def get_subscribers(self):
        recipient_list = []
        recipients_data_dict = self.client.get_belong_recipients_to_group(
            group_id=self.id
        )
        for recipient_data_dict in recipients_data_dict['Items']:
            recipient_data_dict['idList'] = self.list_id
            recipient = Recipient(
                data_dict=recipient_data_dict,
                client=self.client,
                logger=self.logger,
                status='subscribed'
            )
            recipient_list.append(recipient)
        self.logger.debug('Subscribers from group {group_id} retrieved'.format(group_id=self.id))
        return recipient_list

    @client_enabled
    def insert_recipient(self, recipient_id):
        self.client.update_group_subscription(
            group_id=self.id,
            recipient_id=recipient_id,
        )
        self.logger.debug('Recipient {recipient_id} correctly inserted in group {group_id}'.format(
            group_id=self.id,
            recipient_id=recipient_id,
        ))

    @client_enabled
    def extract_recipient(self, recipient_id):
        if recipient_id:
            self.client.update_group_unsubscription(
                group_id=self.id,
                recipient_id=recipient_id,
            )
            self.logger.debug('Recipient {recipient_id} correctly extracted from group {group_id}'.format(
                recipient_id=recipient_id,
                group_id=self.id,
            ))
        else:
            self.logger.error('recipient_id cannot be None'.format(
                recipient_id=recipient_id,
                group_id=self.id,
            ))

    @client_enabled
    def subscribe_recipients_list(self, recipients, confirm_email=False, wait_import=False):
        list_recipient_data_dict = []
        for recipient in recipients:
            list_recipient_data_dict.append(recipient.data_dict)

        import_id = self.client.subscribe_recipients_to_group(
            group_id=self.id,
            list_data_dict=list_recipient_data_dict,
            confirm_email=confirm_email,  # confirm_email=True => "Pending"; confirm_email=False => "Subscribed"
        )
        self.logger.info(
            'Recipients are been subscribed in group {group_id} with import_id={import_id}'.format(
                group_id=self.id,
                import_id=import_id,
            )
        )
        if wait_import:
            # WAITING IMPORT IS COMPLETE
            import_complete = False
            while not import_complete:
                status = self.client.read_import_status(import_id)
                self.logger.warning('Waiting 2 seconds import is complete..')
                time.sleep(2)
                import_complete = status['Completed']
        return import_id

    @client_enabled
    def subscribe_recipients_list_forced(self, recipients, confirm_email=False, wait_import=False):
        list_recipient_data_dict = []
        for recipient in recipients:
            list_recipient_data_dict.append(recipient.data_dict)

        import_id = self.client.subscribe_recipients_to_group(
            group_id=self.id,
            list_data_dict=list_recipient_data_dict,
            confirm_email=confirm_email,  # confirm_email=True => "Pending"; confirm_email=False => "Subscribed"
            import_type="asOptin",
        )
        self.logger.info(
            'Recipients are been subscribed in group {group_id} with import_id={import_id}'.format(
                group_id=self.id,
                import_id=import_id,
            )
        )
        if wait_import:
            # WAITING IMPORT IS COMPLETE
            import_complete = False
            while not import_complete:
                status = self.client.read_import_status(import_id)
                self.logger.warning('Waiting 2 seconds import is complete..')
                time.sleep(2)
                import_complete = status['Completed']
        return import_id

    @client_enabled
    def unsubscribe_recipients_list(self, recipients, wait_import=False):
        list_recipient_data_dict = []
        for recipient in recipients:
            list_recipient_data_dict.append(recipient.data_dict)

        import_id = self.client.unsubscribe_recipients_to_group(
            group_id=self.id,
            list_data_dict=list_recipient_data_dict,
            import_type='asOptout',  # import_type=asOptout: if specified, the given recipients' status is set to "unsubscribe",
        )
        self.logger.info(
            'Recipients are been unsubscribed in group {group_id} with import_id={import_id}'.format(
                group_id=self.id,
                import_id=import_id,
            )
        )
        if wait_import:
            # WAITING IMPORT IS COMPLETE
            import_complete = False
            while not import_complete:
                status = self.client.read_import_status(import_id)
                self.logger.warning('Waiting 2 seconds import is complete..')
                time.sleep(2)
                import_complete = status['Completed']
        return import_id

    @client_enabled
    def send_confirmation_email(self, import_id, send_date=None):
        response = self.client.prepare_to_send_import(import_id)
        sending_info = ast.literal_eval(response)
        sending_id = sending_info['idSending']

        # send_import_sending return other sending info
        other_sending_info = self.client.send_import_sending(
            sending_id=sending_id,
            send_date=send_date
        )
        self.logger.info(
            'Confirmation emails are been sent (sending_id={sending_id}) to import {import_id}'.format(
                sending_id=sending_id,
                import_id=import_id,
            )
        )
        return other_sending_info

    @client_enabled
    def send_message(self, message_id):
        from mailup.providers import MailUpComponentProvider

        provider = MailUpComponentProvider(
            client=self.client,
            logger=self.logger,
        )

        message = provider.get_message(
            list_id=self.list_id,
            message_id=message_id,
        )

        send_statistics = message.send_to_group(
            group_id=self.id,
        )
        return send_statistics

    # PROPERTY
    @property
    def id(self):
        try:
            return self.data_dict['idGroup']
        except KeyError:
            return None

    @id.setter
    def id(self, value):
        self.data_dict['idGroup'] = value


class Recipient(MailUpComponent):

    mailup_pattern_fields = {
        'Name': 'name',
        'Email': 'email',
        'idList': 'list_id',
        'idRecipient': 'recipient_id',
        'Fields': 'fields'
    }

    required_fields = ['Email', 'Name', 'idList']

    def __init__(self, data_dict, client=None, logger=None, status=None, **kwargs):
        # status or recipient: 'subscribed', 'unsubscribed' or 'pending'
        self.status = status
        super(Recipient, self).__init__(data_dict, client, logger, **kwargs)

    def __repr__(self):
        return u'<{class_name}: {email}>'.format(
            class_name=self.__class__.__name__,
            email=self.email,
        )

    # METHODS
    @client_enabled
    def save(self):
        if not self.id:
            self.logger.warning('Recipient {recipient} has no id, a new recipient will be created'.format(
                recipient=self
            ))

            from mailup.providers import MailUpComponentProvider

            provider = MailUpComponentProvider(
                client=self.client,
                logger=self.logger,
            )

            new_recipient = provider.create_recipient(
                data_dict=self.data_dict
            )

            self.data_dict = new_recipient.data_dict
            return self

        saved_data_dict = self.client.update_recipient(
            data_dict=self.data_dict
        )
        saved_data_dict = filter_dict(saved_data_dict, self.mailup_pattern_fields)
        self.data_dict.update(saved_data_dict)
        self.logger.info('Recipient {recipient_id} has been successfully saved'.format(recipient_id=self.id))
        return self

    @client_enabled
    def add_to_list(self, list_id, confirm_email=False):
        self.data_dict['idList'] = list_id

        # response=recipient.id
        response = self.client.add_recipient_to_list(
            list_id=list_id,
            data_dict=self.data_dict,
            confirm_email=confirm_email,
        )
        self.logger.info('Recipient {recipient_id} has been successfully added to List {list_id}'.format(
            recipient_id=self.id,
            list_id=list_id,
        ))
        return self

    @client_enabled
    def subscribe_to_list(self, list_id):
        if not self.id:
            raise exceptions.InvalidRecipientConfigurationException({'idRecipient': None})

        self.data_dict['idList'] = list_id

        # response=recipient.id
        response = self.client.subscribe_recipient_to_list(
            list_id=list_id,
            recipient_id=self.id,
        )
        self.logger.info('Recipient {recipient_id} has been successfully subscribed from List {list_id}'.format(
            recipient_id=self.id,
            list_id=list_id,
        ))
        return self

    @client_enabled
    def unsubscribe_to_list(self, list_id):
        if not self.id:
            raise exceptions.InvalidRecipientConfigurationException({'idRecipient': None})

        self.data_dict['idList'] = list_id

        # response=recipient.id
        response = self.client.unsubscribe_recipient_to_list(
            list_id=list_id,
            recipient_id=self.id,
        )
        self.logger.info('Recipient {recipient_id} has been successfully unsubscribed from List {list_id}'.format(
            recipient_id=self.id,
            list_id=list_id,
        ))
        return self

    @client_enabled
    def add_to_group(self, group_id, confirm_email=False):
        # response=recipient.id
        response = self.client.add_recipient_to_group(
            group_id=group_id,
            data_dict=self.data_dict,
            confirm_email=confirm_email,
        )
        self.logger.info('Recipient {recipient_id} has been successfully Group to group {group_id}'.format(
            recipient_id=self.id,
            group_id=group_id,
        ))
        return self

    # FIELDS METHODS
    def set_field(self, field_name, field_value):
        for field in self.fields:
            if field['Description'] == field_name:
                field['Value'] = field_value
                break

    def get_field(self, field_name):
        for field in self.fields:
            if field['Description'] == field_name:
                return field['Value']

    def set_fields(self, field_dict):
        for key, value in field_dict.iteritems():
            self.set_field(key, value)

    def get_fields(self):
        field_dict = dict()
        fields = self.data_dict['Fields']

        for field in fields:
            key = field['Description']
            value = field['Value']
            field_dict[key] = value

        return field_dict

    # PROPERTY
    @property
    def id(self):
        try:
            return self.data_dict['idRecipient']
        except KeyError:
            return None

    @id.setter
    def id(self, value):
        self.data_dict['idRecipient'] = value


class Message(MailUpComponent):

    mailup_pattern_fields = {
        'Subject': 'subject',
        'idList': 'list_id',
        'idMessage': 'message_id',
        'Content': 'content',
        'Embed': 'embed',
        'Fields': 'fields',
        'IsConfirmation': 'is_confirmation',
        'Notes': 'note',
        'Tags': 'tags',
        'TrackingInfo': 'tracking_info'
    }

    required_fields = ['Subject', 'idList']

    def __repr__(self):
        return u'<{class_name}: {subject}>'.format(
            class_name=self.__class__.__name__,
            subject=self.subject,
        )

    # METHODS
    def save(self):
        if not self.id:
            self.logger.warning('Message {message} has no id, a new message will be created'.format(message=self))

            from mailup.providers import MailUpComponentProvider

            provider = MailUpComponentProvider(
                client=self.client,
                logger=self.logger,
            )
            new_message = provider.create_message(
                data_dict=self.data_dict
            )
            self.data_dict = new_message.data_dict
            return self
        detail_data_dict = self.client.read_message_detail(
            list_id=self.list_id,
            message_id=self.id
        )
        detail_data_dict.update(self.data_dict)
        self.data_dict.update(detail_data_dict)
        saved_data_dict = self.client.update_message(
            list_id=self.list_id,
            message_id=self.id,
            data_dict=self.data_dict,
        )
        saved_data_dict = filter_dict(saved_data_dict, self.mailup_pattern_fields)
        self.data_dict.update(saved_data_dict)
        self.logger.info('Message {message_id} has been successfully saved'.format(message_id=self.id))
        return self

    @client_enabled
    def send_to_list(self, list_id):
        send_statistic = self.client.send_message_to_list(
            list_id=list_id,
            message_id=self.id,
        )
        return ast.literal_eval(send_statistic)

    @client_enabled
    def send_to_group(self, group_id):
        send_statistic = self.client.send_message_to_group(
            group_id=group_id,
            message_id=self.id,
        )
        return ast.literal_eval(send_statistic)

    @client_enabled
    def send_to_recipient(self, recipient_id):
        from mailup.providers import MailUpComponentProvider

        provider = MailUpComponentProvider(
            client=self.client,
            logger=self.logger,
        )
        recipient = provider.get_recipient(
            list_id=self.list_id,
            recipient_id=recipient_id
        )
        send_statistic = self.client.send_message_to_recipient(
            email=recipient.email,
            message_id=self.id,
        )
        return send_statistic

    # FIELDS METHODS
    def set_field(self, field_name, field_value):
        for field in self.fields:
            if field['Description'] == field_name:
                field['Value'] = field_value
                break

    def get_field(self, field_name):
        for field in self.fields:
            if field['Description'] == field_name:
                return field['Value']

    def set_fields(self, field_dict):
        for key, value in field_dict.iteritems():
            self.set_field(key, value)

    def get_fields(self):
        field_dict = dict()
        fields = self.data_dict['Fields']

        for field in fields:
            key = field['Description']
            value = field['Value']
            field_dict[key] = value

        return field_dict

    # PROPERTY
    @property
    def id(self):
        try:
            return self.data_dict['idMessage']
        except KeyError:
            return None

    @id.setter
    def id(self, value):
        self.data_dict['idMessage'] = value


class Tag(MailUpComponent):

    mailup_pattern_fields = {
        'Id': 'tag_id',
        'Name': 'name',
        'idList': 'list_id',  # not in mailup data_dict
    }

    required_fields = ['Name', 'idList']

    def __repr__(self):
        return u'<{class_name}: {name}>'.format(
            class_name=self.__class__.__name__,
            name=self.name,
        )

    # METHODS
    def save(self):
        if not self.id:
            self.logger.warning('Tag {tag} has no id, a new tag will be created'.format(tag=self))

            from mailup.providers import MailUpComponentProvider

            provider = MailUpComponentProvider(
                client=self.client,
                logger=self.logger,
            )
            new_tag = provider.create_tag(
                data_dict=self.data_dict
            )
            self.data_dict = new_tag.data_dict
            return self

        saved_data_dict = self.client.modify_tag(
            list_id=self.list_id,
            data_dict=self.data_dict,
        )

        saved_data_dict = filter_dict(saved_data_dict, self.mailup_pattern_fields)
        self.data_dict.update(saved_data_dict)
        self.logger.info('Tag {tag_id} has been successfully saved'.format(tag_id=self.id))
        return self

    # PROPERTY
    @property
    def id(self):
        try:
            return self.data_dict['Id']
        except KeyError:
            return None

    @id.setter
    def id(self, value):
        self.data_dict['Id'] = value


class Attachment(MailUpComponent):

    mailup_pattern_fields = {
        'Name': 'name',
        'Base64Data': 'base_64_data',
        'Path': 'path',
        'Slot': 'slot',
        'idList': 'list_id',
        'idMessage': 'message_id',  # not in mailup data_dict
    }

    required_fields = ['Slot', 'idMessage']

    def __repr__(self):
        return u'<{class_name}: {name}>'.format(
            class_name=self.__class__.__name__,
            name=self.name,
        )

    def save(self):
        pass

    # PROPERTY
    @property
    def id(self):
        self.logger.warning('Attachment as not a id in MailUp. Use message_id and slot or file name.')
        return None

    @id.setter
    def id(self, value):
        self.logger.error('Attachment as not a id in MailUp. Use message_id and slot or file name.')
