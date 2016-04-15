# coding: UTF-8
import time

from mailup import exceptions

from mailup.logger import LoggerSingleton


class MailUpComponentProvider(object):
    client = None
    logger = None

    def __init__(self, client, logger=None):
        # CLIENT INITIALISATION
        self.client = client

        # LOGGER INITIALISATION
        if logger:
            self.logger = logger
        else:
            self.logger = LoggerSingleton()
            self.logger.disabled = True

        super(MailUpComponentProvider, self).__init__()

    # LIST PROVIDER METHODS
    def create_list(self, data_dict):
        from mailup.components import List

        # check data_dict, not valid InvalidConfigurationException is rise
        List(data_dict, required_fields=['Name', 'owneremail', 'replyto'])

        # Default List parameter
        if 'useDefaultSettings' not in data_dict:
            data_dict['useDefaultSettings'] = False
        if 'idSettings' not in data_dict:
            data_dict['idSettings'] = 1
        if 'business' not in data_dict:
            data_dict['business'] = True
        if 'Customer' not in data_dict:
            data_dict['Customer'] = True
        if 'scope' not in data_dict:
            data_dict['scope'] = "newsletters"
        if 'format' not in data_dict:
            data_dict['format'] = "html"
        if 'copyTemplate' not in data_dict:
            data_dict['copyTemplate'] = True
        if 'copyWebhooks' not in data_dict:
            data_dict['copyWebhooks'] = True
        if 'charset' not in data_dict:
            data_dict['charset'] = "UTF-8"
        if 'public' not in data_dict:
            data_dict['public'] = True
        if 'tracking' not in data_dict:
            data_dict['tracking'] = True
        if 'optout_type' not in data_dict:
            data_dict['optout_type'] = 0
        if 'sendemailoptout' not in data_dict:
            data_dict['sendemailoptout'] = False
        if 'frontendform' not in data_dict:
            data_dict['frontendform'] = True
        if 'headerxabuse' not in data_dict:
            data_dict['headerxabuse'] = "Please report abuse here: http://[host]/p"
        if 'kbmax' not in data_dict:
            data_dict['kbmax'] = 100
        if 'headerlistunsubscriber' not in data_dict:
            data_dict['headerlistunsubscriber'] = "<[listunsubscribe]>,<[mailto_uns]>"
        if 'multipart_text' not in data_dict:
            data_dict['multipart_text'] = True
        if 'subscribedemail' not in data_dict:
            data_dict['subscribedemail'] = True
        if 'sendconfirmsms' not in data_dict:
            data_dict['sendconfirmsms'] = False
        list_id = self.client.create_list(
            data_dict=data_dict
        )

        # provider = MailUpComponentProvider(client=self.client)
        # provided_list = None
        # while not provided_list:
        #     provided_list = provider.get_list(list_id)
        #     if not provided_list:
        #         self.logger.warning('List just created is not ready yet')
        #         time.sleep(2)

        self.logger.info('List with id {list_id} created successfully'.format(list_id=list_id))
        return self.get_list(list_id)

    def get_list(self, list_id):
        from mailup.components import List

        items = self.client.read_lists(filters={'idList': list_id})['Items']
        if not items:
            self.logger.debug('List with id {list_id} found'.format(list_id=list_id))
            raise exceptions.ListNotFoundException(list_id)

        data_dict = items[0]
        return List(
            data_dict=data_dict,
            client=self.client,
            logger=self.logger
        )

    def all_lists(self):
        from mailup.components import List

        paginated_data_dicts = self.client.read_lists()
        all_lists = []
        data_dicts = paginated_data_dicts['Items']
        for data_dict in data_dicts:
            new_list = List(
                data_dict=data_dict,
                client=self.client,
                logger=self.logger
            )
            all_lists.append(new_list)
        self.logger.debug('{count} Lists founds'.format(count=len(all_lists)))
        return all_lists

    def filter_lists(self, filters):
        from mailup.components import List

        paginated_data_dicts = self.client.read_lists(filters=filters)
        filtered_lists = []
        data_dicts = paginated_data_dicts['Items']
        for data_dict in data_dicts:
            new_list = List(
                data_dict=data_dict,
                client=self.client,
                logger=self.logger
            )
            filtered_lists.append(new_list)
        self.logger.debug('{count} Lists founds'.format(count=len(filtered_lists)))
        return filtered_lists

    # GROUP PROVIDER METHODS
    def create_group(self, data_dict):
        from mailup.components import Group

        # check data_dict, not valid InvalidConfigurationException is rise
        Group(data_dict)

        list_id = data_dict['idList']

        new_data_dict = self.client.create_group(
            list_id=list_id,
            data_dict=data_dict,
        )
        new_group = Group(
            data_dict=new_data_dict,
            client=self.client,
            logger=self.logger
        )
        self.logger.info('Group {new_group} created successfully'.format(new_group=new_group))
        return new_group

    def get_group(self, list_id, group_id):
        from mailup.components import Group

        items = self.client.read_groups(
            list_id=list_id,
            filters={'idGroup': group_id},
        )['Items']

        if not items:
            self.logger.debug('Group with id {group_id} found'.format(group_id=group_id))
            raise exceptions.GroupNotFoundException(group_id)

        data_dict = items[0]
        return Group(
            data_dict=data_dict,
            client=self.client,
            logger=self.logger
        )

    def all_groups(self, list_id):
        from mailup.components import Group

        data_dicts = []
        groups_data_dict = self.client.read_groups(list_id=list_id)
        for data_dict in groups_data_dict['Items']:
            group = Group(
                data_dict=data_dict,
                client=self.client,
                logger=self.logger
            )
            data_dicts.append(group)
        self.logger.debug('{count} Groups founds'.format(count=len(data_dicts)))
        return data_dicts

    def filter_groups(self, list_id, filters):
        from mailup.components import Group

        data_dicts = self.client.read_groups(
            list_id=list_id,
            filters=filters
        )
        filtered_groups = []
        data_dicts = data_dicts['Items']
        for data_dict in data_dicts:
            new_group = Group(
                data_dict=data_dict,
                client=self.client,
                logger=self.logger
            )
            filtered_groups.append(new_group)
        self.logger.debug('{count} Groups founds'.format(count=len(filtered_groups)))
        return filtered_groups

    # RECIPIENT PROVIDER METHODS
    def create_recipient(self, data_dict, confirm_email=False):
        from mailup.components import Recipient

        if confirm_email:
            status = 'pending'
        else:
            status = 'subscribed'

        # check data_dict, not valid InvalidConfigurationException is rise
        Recipient(data_dict)

        list_id = data_dict['idList']

        recipient = Recipient(
            data_dict=data_dict,
            client=self.client,
            logger=self.logger,
            status=status,
        )
        email = recipient.email
        try:
            recipient = self.get_recipient(list_id=list_id, email=email, write_log=False)
            if recipient:
                raise exceptions.RecipientAlreadyExistException(
                    list_id=list_id,
                    email=email,
                )
        except exceptions.RecipientNotFoundException:
            recipient_id = self.client.add_recipient_to_list(
                list_id=list_id,
                data_dict=recipient.data_dict,
                confirm_email=confirm_email
            )
            recipient.data_dict['idRecipient'] = recipient_id
            self.logger.info('Recipient {new_recipient} created successfully'.format(
                new_recipient=recipient
            ))
            return recipient

    def get_recipient(self, list_id, recipient_id=None, email=None, status=None, write_log=True):
        from mailup.components import Recipient

        filters = {}

        if recipient_id:
            filters['idRecipient'] = recipient_id

        if email:
            filters['Email'] = email

        if not filters:
            self.logger.warning('"get_recipient" without "recipient_id" or "email"')
            return None

        for status_tried in ['subscribed', 'unsubscribed', 'pending']:
            if status == status_tried or not status:
                data_dicts = self.client.get_recipients(
                    list_id=list_id,
                    filters=filters,
                    status=status_tried,
                )['Items']
                if data_dicts:
                    data_dict = data_dicts[0]
                    if data_dict:
                        data_dict['idList'] = list_id
                        return Recipient(
                            data_dict=data_dict,
                            client=self.client,
                            logger=self.logger,
                            status=status_tried,
                        )
        raise exceptions.RecipientNotFoundException(
            recipient_id=recipient_id,
            email=email,
            status=status,
            write_log=write_log
        )

    def all_recipients_subscribed(self, list_id):
        from mailup.components import Recipient
        recipient_list = []

        data_dicts = self.client.get_recipients(
            list_id=list_id,
            status='subscribed',
        )['Items']
        if data_dicts:
            for data_dict in data_dicts:
                data_dict['idList'] = list_id
                recipient = Recipient(
                    data_dict=data_dict,
                    client=self.client,
                    logger=self.logger,
                    status='subscribed',
                )
                recipient_list.append(recipient)
        return recipient_list

    def all_recipients_unsubscribed(self, list_id):
        from mailup.components import Recipient
        recipient_list = []

        data_dicts = self.client.get_recipients(
            list_id=list_id,
            status='unsubscribed',
        )['Items']
        if data_dicts:
            for data_dict in data_dicts:
                data_dict['idList'] = list_id
                recipient = Recipient(
                    data_dict=data_dict,
                    client=self.client,
                    logger=self.logger,
                    status='unsubscribed',
                )
                recipient_list.append(recipient)
        return recipient_list

    def all_recipients_pending(self, list_id):
        from mailup.components import Recipient
        recipient_list = []

        data_dicts = self.client.get_recipients(
            list_id=list_id,
            status='pending',
        )['Items']
        if data_dicts:
            for data_dict in data_dicts:
                data_dict['idList'] = list_id
                recipient = Recipient(
                    data_dict=data_dict,
                    client=self.client,
                    logger=self.logger,
                    status='pending',
                )
                recipient_list.append(recipient)
        return recipient_list

    def all_recipients(self, list_id):
        subscribed_recipients = self.all_recipients_subscribed(list_id=list_id)
        unsubscribed_recipients = self.all_recipients_unsubscribed(list_id=list_id)
        pending_recipients = self.all_recipients_pending(list_id=list_id)
        all_recipient = subscribed_recipients + unsubscribed_recipients + pending_recipients
        self.logger.debug('{count} Recipient founds'.format(count=len(all_recipient)))
        return all_recipient

    def filter_recipients(self, list_id, filters, status=None):
        from mailup.components import Recipient
        recipient_list = []

        if status:
            data_dicts = self.client.get_recipients(
                list_id=list_id,
                status=status,
                filters=filters,
            )['Items']
            for data_dict in data_dicts:
                data_dict['idList'] = list_id
                recipient = Recipient(
                    data_dict=data_dict,
                    client=self.client,
                    logger=self.logger,
                    status=status,
                )
                recipient_list.append(recipient)
            return recipient_list
        else:
            for status_tried in ['subscribed', 'unsubscribed', 'pending']:
                data_dicts = self.client.get_recipients(
                    list_id=list_id,
                    status=status_tried,
                    filters=filters,
                )['Items']
                for data_dict in data_dicts:
                    data_dict['idList'] = list_id
                    recipient = Recipient(
                        data_dict=data_dict,
                        client=self.client,
                        logger=self.logger,
                        status=status_tried,
                    )
                    recipient_list.append(recipient)
            return recipient_list

    # MESSAGE PROVIDER METHODS
    def create_message(
            self, data_dict, content='', embed=False, is_confirmation=False, tracking_info=None
    ):
        from mailup.components import Message

        # check data_dict, not valid InvalidConfigurationException is rise
        Message(data_dict)

        list_id = data_dict['idList']

        data_dict['Content'] = content
        data_dict['Embed'] = embed
        data_dict['IsConfirmation'] = is_confirmation
        if tracking_info:
            data_dict['TrackingInfo'] = tracking_info
        else:
            data_dict['TrackingInfo'] = {
                'CustomParams': '',
                'Enabled': False,
                'Protocols': ['http:', 'https:', 'ftp:', 'news:'],
            }

        response = self.client.create_message(
            list_id=list_id,
            data_dict=data_dict
        )

        new_data_dict = response
        new_message = Message(
            data_dict=new_data_dict,
            client=self.client,
            logger=self.logger,
        )
        self.logger.info('Message {new_message} create successfully'.format(new_message=new_message))
        return new_message

    def get_message(self, list_id, message_id):
        from mailup.components import Message

        try:
            data_dict = self.client.read_message_detail(list_id, message_id)
            message = Message(
                data_dict=data_dict,
                client=self.client,
                logger=self.logger,
            )
            return message
        except exceptions.MailUpCallError:
            raise exceptions.MessageNotFoundException(message_id=message_id)

    def all_messages(self, list_id, status=None):
        from mailup.components import Message

        data_dicts = self.client.list_messages(
            list_id=list_id,
            status=status,
        )
        all_messages = []
        messages_data_dict = data_dicts['Items']
        for data_dict in messages_data_dict:
            message = Message(
                data_dict=data_dict,
                client=self.client,
                logger=self.logger,
            )
            all_messages.append(message)
        self.logger.debug('Messages found')
        return all_messages

    def all_published_messages(self, list_id):
        return self.all_messages(list_id=list_id, status='Online')

    def all_archived_messages(self, list_id):
        return self.all_messages(list_id=list_id, status='Archived')

    def filter_messages(self, list_id, status=None, filters=None):
        from mailup.components import Message

        data_dicts = self.client.list_messages(
            list_id=list_id,
            status=status,
            filters=filters,
        )
        all_messages = []
        messages_data_dict = data_dicts['Items']
        for data_dict in messages_data_dict:
            message = Message(
                data_dict=data_dict,
                client=self.client,
                logger=self.logger,
            )
            all_messages.append(message)
        self.logger.debug('Messages found')
        return all_messages

    # TAG PROVIDER METHOD
    def create_tag(self, data_dict):
        from mailup.components import Tag

        # check data_dict, not valid InvalidConfigurationException is rise
        Tag(data_dict)
        list_id = data_dict['idList']
        tag_name = data_dict['Name']

        try:
            self.get_tag(list_id, tag_name=tag_name, write_log=False)
            raise exceptions.TagAlreadyExistException(
                list_id=list_id,
                tag_name=tag_name,
            )
        except exceptions.TagNotFoundException:
            response = self.client.create_tag(
                list_id=list_id,
                tag_name=data_dict['Name'],
            )
            new_data_dict = response
            new_data_dict['idList'] = list_id
            new_tag = Tag(
                data_dict=new_data_dict,
                client=self.client,
                logger=self.logger
            )
            self.logger.info('Tag {new_tag} created successfully'.format(new_tag=new_tag))
            return new_tag

    def get_tag(self, list_id, tag_id=None, tag_name=None, write_log=True):
        from mailup.components import Tag

        if not tag_id and not tag_name:
            return self.all_tags(list_id)
        tags_data_paginated = self.client.list_tags(list_id=list_id, tag_id=tag_id, tag_name=tag_name)
        if tags_data_paginated and tags_data_paginated['TotalElementsCount'] > 0:
            data_dict = tags_data_paginated['Items'][0]
            data_dict['idList'] = list_id
            tag = Tag(
                data_dict=data_dict,
                client=self.client,
                logger=self.logger
            )
            self.logger.debug('Tag with id {tag_id} found'.format(tag_id=tag_id))
            return tag
        else:
            raise exceptions.TagNotFoundException(
                tag_id=tag_id,
                tag_name=tag_name,
                write_log=write_log
            )

    def all_tags(self, list_id):
        from mailup.components import Tag

        tags_list = []
        tags_data_dict = self.client.list_tags(list_id=list_id)
        for data_dict in tags_data_dict['Items']:
            # Mailup not get (in this case) 'idList' in data_dict
            data_dict['idList'] = list_id

            # check data_dict, not valid InvalidConfigurationException is rise
            tag = Tag(
                data_dict=data_dict,
                client=self.client,
                logger=self.logger
            )
            tags_list.append(tag)
        self.logger.debug('{count} Tags founds'.format(count=len(tags_list)))
        return tags_list

    # ATTACHMENT PROVIDER METHODS
    def all_attachments(self, list_id, message_id):
        from mailup.components import Attachment

        attachments_list = []
        attachments_data_dict = self.client.read_message_attachments(
            list_id=list_id,
            message_id=message_id,
        )
        for attachment_data_dict in attachments_data_dict:
            # Mailup not get (in this case) 'idList' and 'idMessage' in data_dict
            attachment_data_dict['idList'] = list_id
            attachment_data_dict['idMessage'] = message_id
            attachment = Attachment(
                data_dict=attachment_data_dict,
                client=self.client,
                logger=self.logger,
            )
            attachments_list.append(attachment)
        self.logger.debug('{count} Attachments founds'.format(count=len(attachments_list)))
        return attachments_list

    def get_attachment(self, list_id, message_id, file_name=None, slot=None):
        if not file_name and not slot:
            return 'Please indicate file name or file slot to find attachment'
        elif slot and not 1 <= slot <= 5:
            return 'Please indicate a slot >= 1 and <= 5'

        all_attachments = self.all_attachments(list_id, message_id)
        for attachment in all_attachments:
            if attachment.name == file_name or attachment.slot == slot:
                return attachment
        raise exceptions.AttachmentNotFoundException(slot, file_name)
