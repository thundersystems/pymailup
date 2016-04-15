# coding: utf-8

import ast
from mailup.logger import LoggerSingleton


# GENERIC EXCEPTION
class MailUpException(Exception):
    error_text = None

    def __init__(self, write_log):
        # critical log
        self.logger = LoggerSingleton()
        if write_log:
            self.logger.error(self.error_text)

    def __str__(self):
        return repr(self.error_text)

    def __repr__(self):
        return repr(self.error_text)


# CLIENT
class ClientNotEnabledException(MailUpException):
    """
    To import:
        import exceptions

    To declare in a class add a class attribute:
        ClientNotEnabledException = exceptions.ClientNotEnabledException

    To raise:
        raise self.ClientNotEnabledException()
    """

    def __init__(self, error_text, write_log=True):
        self.error_text = error_text
        super(ClientNotEnabledException, self).__init__(write_log)


class MailUpCallError(MailUpException):
    """
    To import:
        import exceptions

    To declare in a class add a class attribute:
        MailUpCallError = exceptions.MailUpCallError

    To raise:
        raise self.MailUpCallError(req)
    """

    def __init__(self, error_text, write_log=True):
        self.error_text = error_text
        super(MailUpCallError, self).__init__(write_log)

    @staticmethod
    def unicode_to_dict(unicode_dict):
        unicode_dict = unicode_dict.replace(':null', ':None')
        unicode_dict = unicode_dict.replace(':false', ':False')
        unicode_dict = unicode_dict.replace(':true', ':True')
        dictionary = ast.literal_eval(unicode_dict)
        return dictionary


# ALL COMPONENTS
class ListNotSpecifiedException(MailUpException):
    """
    To import:
        import exceptions

    To declare in a class add a class attribute:
        ListNotSpecifiedException = exceptions.ListNotSpecifiedException

    To raise:
        raise self.ListNotSpecifiedException()
    """

    def __init__(self):
        self.error_text = '"idList" element not specified in data_dict'
        super(ListNotSpecifiedException, self).__init__()


class InvalidConfigurationException(MailUpException):
    """
    To import:
        import exceptions

    To declare in a class add a class attribute:
        InvalidConfigurationException = exceptions.InvalidConfigurationException

    To raise:
        raise self.InvalidConfigurationException(dict())
    """

    def __init__(self, parameter_dict, write_log=True):
        parameters_str = [
            '{key}={value}'.format(key=key, value=value) for key, value in parameter_dict.iteritems()
        ]
        self.error_text = 'Invalid configuration for one or more parameters in data_dict: {parameters}'.format(
            parameters=parameters_str
        )
        super(InvalidConfigurationException, self).__init__(write_log)


# RECIPIENT
class RecipientNotFoundException(MailUpException):
    """
    To import:
        import exceptions

    To declare in a class add a class attribute:
        RecipientNotFoundException = exceptions.RecipientNotFoundException

    To raise:
        raise self.RecipientNotFoundException(recipient_id)
    """

    def __init__(self, recipient_id=None, email=None, status=None, write_log=True):
        self.error_text = 'MailUp recipient with id "{recipient_id}" and email "{email}"{status_message} not found'.format(
            recipient_id=recipient_id,
            email=email,
            status_message=' in status "{status}"'.format(status=status) if status else ''
        )
        super(RecipientNotFoundException, self).__init__(write_log)


class InvalidRecipientConfigurationException(MailUpException):
    """
    To import:
        import exceptions

    To declare in a class add a class attribute:
        InvalidRecipientConfigurationException = exceptions.InvalidRecipientConfigurationException

    To raise:
        raise self.InvalidRecipientConfigurationException(dict())
    """

    def __init__(self, parameter_dict, write_log=True):
        parameters_str = [
            '{key}={value}'.format(key=key, value=value) for key, value in parameter_dict.iteritems()
        ]
        self.error_text = 'Invalid configuration for one or more parameters in recipient_data_dict: {parameters}'.format(
            parameters=parameters_str
        )
        super(InvalidRecipientConfigurationException, self).__init__(write_log)


class InvalidRecipientStatusException(MailUpException):
    """
    To import:
        import exceptions

    To declare in a class add a class attribute:
        InvalidRecipientStatusException = exceptions.InvalidRecipientStatusException

    To raise:
        raise self.InvalidRecipientStatusException(status)
    """

    def __init__(self, status, write_log=True):
        self.error_text = '"{status}" is a invalid status for recipient'.format(status=status)
        super(InvalidRecipientStatusException, self).__init__(write_log)


class RecipientAlreadyExistException(MailUpException):
    """
    To import:
        import exceptions

    To declare in a class add a class attribute:
        RecipientAlreadyExistException = exceptions.RecipientAlreadyExistException

    To raise:
        raise self.RecipientAlreadyExistException(recipient_id, recipient_email)
    """
    def __init__(self, list_id, id=None, email=None, write_log=True):
        self.error_text = 'Recipient with{recipient_id_error}{recipient_email_error} already exists in list: {list_id}'.format(
            recipient_id_error=' id "{recipient_id}"{and_also}'.format(
                recipient_id=id,
                and_also=' and ' if email else '',
            ) if id else '',
            recipient_email_error=' name "{recipient_email}"'.format(
                recipient_email=email,
            ) if email else '',
            list_id=list_id,
        )
        super(RecipientAlreadyExistException, self).__init__(write_log)


# GROUP
class GroupNotFoundException(MailUpException):
    """
    To import:
        import exceptions

    To declare in a class add a class attribute:
        GroupNotFoundException = exceptions.GroupNotFoundException

    To raise:
        raise self.GroupNotFoundException(group_id)
    """

    def __init__(self, group_id, write_log=True):
        self.error_text = 'MailUp group with id {group_id} not found'.format(group_id=group_id)
        super(GroupNotFoundException, self).__init__(write_log)


class InvalidGroupConfigurationException(MailUpException):
    """
    To import:
        import exceptions

    To declare in a class add a class attribute:
        InvalidGroupConfigurationException = exceptions.InvalidGroupConfigurationException

    To raise:
        raise self.InvalidGroupConfigurationException(dict())
    """

    def __init__(self, parameter_dict, write_log=True):
        parameters_str = [
            '{key}={value}'.format(key=key, value=value) for key, value in parameter_dict.iteritems()
        ]
        self.error_text = 'Invalid configuration for one or more parameters in group_data_dict: {parameters}'.format(
            parameters=parameters_str
        )
        super(InvalidGroupConfigurationException, self).__init__(write_log)


# LIST
class ListNotFoundException(MailUpException):
    """
    To import:
        import exceptions

    To declare in a class add a class attribute:
        ListNotFoundException = exceptions.ListNotFoundException

    To raise:
        raise self.ListNotFoundException(list_id)
    """

    def __init__(self, list_id, write_log=True):
        self.error_text = 'MailUp list with id {id_list} not found'.format(id_list=list_id)
        super(ListNotFoundException, self).__init__(write_log)


class InvalidListConfigurationException(MailUpException):
    """
    To import:
        import exceptions

    To declare in a class add a class attribute:
        InvalidListConfigurationException = exceptions.InvalidListConfigurationException

    To raise:
        raise self.InvalidListConfigurationException(dict())
    """

    def __init__(self, parameter_dict, write_log=True):
        parameters_str = [
            '{key}={value}'.format(key=key, value=value) for key, value in parameter_dict.iteritems()
        ]
        self.error_text = 'Invalid configuration for one or more parameters in list_data_dict: {parameters}'.format(
            parameters=parameters_str
        )
        super(InvalidListConfigurationException, self).__init__(write_log)


# LIST / GROUP
class IdImportDoesNotExists(MailUpException):
    """
    To import:
        import exceptions

    To declare in a class add a class attribute:
        IdImportDoesNotExists = exceptions.IdImportDoesNotExists

    To raise:
        raise self.IdImportDoesNotExists()
    """

    def __init__(self, write_log=True):
        self.error_text = 'Missing idImport'
        super(IdImportDoesNotExists, self).__init__(write_log)


# MESSAGE
class MessageNotFoundException(MailUpException):
    """
    To import:
        import exceptions

    To declare in a class add a class attribute:
        MessageNotFoundException = exceptions.MessageNotFoundException

    To raise:
        raise self.MessageNotFoundException(message_id)
    """

    def __init__(self, message_id, write_log=True):
        self.error_text = 'MailUp message with id {message_id} not found'.format(message_id=message_id)
        super(MessageNotFoundException, self).__init__(write_log)


class InvalidMessageConfigurationException(MailUpException):
    """
    To import:
        import exceptions

    To declare in a class add a class attribute:
        InvalidMessageConfigurationException = exceptions.InvalidMessageConfigurationException

    To raise:
        raise self.InvalidMessageConfigurationException(dict())
    """

    def __init__(self, parameter_dict, write_log=True):
        parameters_str = [
            '{key}={value}'.format(key=key, value=value) for key, value in parameter_dict.iteritems()
        ]
        self.error_text = 'Invalid configuration for one or more parameters in message_data_dict: {parameters}'.format(
            parameters=parameters_str
        )
        super(InvalidMessageConfigurationException, self).__init__(write_log)


# TAG
class TagNotFoundException(MailUpException):
    """
    To import:
        import exceptions

    To declare in a class add a class attribute:
        TagNotFoundException = exceptions.TagNotFoundException

    To raise:
        raise self.TagNotFoundException(tag_id)
    """

    def __init__(self, tag_id=None, tag_name=None, write_log=True):
        self.error_text = 'MailUp tag with id "{tag_id}" and name "{tag_name}" not found'.format(
            tag_id=tag_id,
            tag_name=tag_name,
        )
        super(TagNotFoundException, self).__init__(write_log)


class InvalidTagConfigurationException(MailUpException):
    """
    To import:
        import exceptions

    To declare in a class add a class attribute:
        InvalidTagConfigurationException = exceptions.InvalidTagConfigurationException

    To raise:
        raise self.InvalidTagConfigurationException(dict())
    """

    def __init__(self, parameter_dict, write_log=True):
        parameters_str = [
            '{key}={value}'.format(key=key, value=value) for key, value in parameter_dict.iteritems()
        ]
        self.error_text = 'Invalid configuration for one or more parameters in tag_data_dict: {parameters}'.format(
            parameters=parameters_str
        )
        super(InvalidTagConfigurationException, self).__init__(write_log)


class TagAlreadyExistException(MailUpException):
    """
    To import:
        import exceptions

    To declare in a class add a class attribute:
        TagAlreadyExistException = exceptions.TagAlreadyExistException

    To raise:
        raise self.TagAlreadyExistException(tag_id, tag_name)
    """
    def __init__(self, list_id, tag_id=None, tag_name=None, write_log=True):
        self.error_text = 'Tag with{tag_id_error}{tag_name_error} already exists in list: {list_id}'.format(
            tag_id_error=' id "{tag_id}"{and_also}'.format(
                tag_id=tag_id,
                and_also=' and ' if tag_name else '',
            ) if tag_id else '',
            tag_name_error=' name "{tag_name}"'.format(
                tag_name=tag_name,
            ) if tag_name else '',
            list_id=list_id,
        )
        super(TagAlreadyExistException, self).__init__(write_log)


# ATTACHMENT
class AttachmentNotFoundException(MailUpException):
    """
    To import:
        import exceptions

    To declare in a class add a class attribute:
        AttachmentNotFoundException = exceptions.AttachmentNotFoundException

    To raise:
        raise self.AttachmentNotFoundException(attachment_id)
    """

    def __init__(self, slot=None, file_name=None, write_log=True):

        if slot and file_name:
            self.error_text = 'MailUp attachment with slot {slot} and file_name = {file_name} not found'.format(
                slot=slot,
                file_name=file_name,
            )
        elif slot:
            self.error_text = 'MailUp attachment with slot {slot} not found'.format(
                slot=slot,
            )
        elif file_name:
            self.error_text = 'MailUp attachment with file_name = {file_name} not found'.format(
                file_name=file_name,
            )
        else:
            self.error_text = 'MailUp attachment not found'
        super(AttachmentNotFoundException, self).__init__(write_log)


class InvalidAttachmentConfigurationException(MailUpException):
    """
    To import:
        import exceptions

    To declare in a class add a class attribute:
        InvalidAttachmentConfigurationException = exceptions.InvalidAttachmentConfigurationException

    To raise:
        raise self.InvalidAttachmentConfigurationException(dict())
    """

    def __init__(self, parameter_dict, write_log=True):
        parameters_str = [
            '{key}={value}'.format(key=key, value=value) for key, value in parameter_dict.iteritems()
        ]
        self.error_text = 'Invalid configuration for one or more parameters in attachment_data_dict: {parameters}'.format(
            parameters=parameters_str
        )
        super(InvalidAttachmentConfigurationException, self).__init__(write_log)
