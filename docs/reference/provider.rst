Provider
========

The *provider* offers the *get*, *create*, *all* and *filters* methods for objects: *lists*, *groups*, *recipient*,
*messages*, *attachments*, *tags*.



create_list
+++++++++++

.. py:function:: create_list(data_dict)

   Create a List on Mailup

   :param dict data_dict: data dict of list
   :return: List instance
   :rtype: List
   :raises InvalidListConfigurationException: bad data dict
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API

get_list
++++++++

.. py:function:: get_list(list_id)

   Retrieve a List instance with id = *list_id*

   :param int list_id: id of list
   :return: List instance
   :rtype: List
   :raises ListNotFoundException: if a list with id = *list_id* does not exists on your MailUp account
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


all_lists
+++++++++

.. py:function:: all_lists()

   Retrieve a instance list of all List on your MailUp account

   :return: instance list
   :rtype: list
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


filter_lists
++++++++++++

.. py:function:: filter_lists(filters)

   Retrieve a instance list of all List on MailUp filtered by *filters* dict; *filters* is structured like data_dict,
   in fact you can use own *data_dict*. The '==' operator is applied (refer to
   `MailUp documentation <http://help.mailup.com/display/mailupapi/Paging+and+filtering#Pagingandfiltering-Filtering>`_ for detail.)

   :return: instance list
   :rtype: list
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


create_group
++++++++++++

.. py:function:: create_group(data_dict)

   Create a Group on List, List on which it is created is defined in *data_dict*

   :param dict data_dict: data dict of group
   :return: Group instance
   :rtype: Group
   :raises InvalidGroupConfigurationException: bad data dict
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


get_group
+++++++++

.. py:function:: get_group(list_id, group_id)

   Retrieve a Group in a List with id *list_id* instance with id = *group_id*

   :param int list_id: id of the List in which to retrieve the group
   :param int group_id: id of group to retrieve
   :return: Group instance
   :rtype: Group
   :raises GroupNotFoundException: if a group with id = *group_id* does not exists on list with id = *list_id*
   :raises ListNotFoundException: if a list with id = *list_id* does not exists on your MailUp account
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


all_groups
++++++++++

.. py:function:: all_groups(list_id)

   Retrieve a instance list of all Group on List with id = *list_id*

   :param int list_id: id of the List in which to retrieve the group list
   :return: list of Group instance
   :rtype: list
   :raises ListNotFoundException: if a list with id = *list_id* does not exists on your MailUp account
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


filter_groups
+++++++++++++

.. py:function:: filter_groups(list_id, filters)

   Retrieve a instance list of all Group on List with id=list_id filtered by *filters* dict; *filters* is structured like data_dict,
   in fact you can use own *data_dict*. The '==' operator is applied (refer to
   `MailUp documentation <http://help.mailup.com/display/mailupapi/Paging+and+filtering#Pagingandfiltering-Filtering>`_ for detail.)

   :return: instance list
   :rtype: list
   :raises ListNotFoundException: if a list with id = *list_id* does not exists on your MailUp account
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


create_recipient
++++++++++++++++

.. py:function:: create_recipient(recipient_data_dict, confirm_email=False)

   Create a Recipient on List, List on which it is created is defined in *recipient_data_dict*

   :param dict recipient_data_dict: data dict of recipient
   :param bool confirm_email: refer to `MailUp documentation <http://help.mailup.com/display/mailupapi/Recipients#Recipients-Manageasingleemailrecipient/subscriber>`_
   :return: Recipient instance
   :rtype: Recipient
   :raises InvalidRecipientConfigurationException: bad data dict
   :raises RecipientAlreadyExistException: email of recipient to create already exists in list
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


get_recipient
+++++++++++++

.. py:function:: get_recipient(list_id, recipient_id=None, email=None, status=None)

   Retrieve a Recipient in a List with id *list_id* instance with id = *group_id* and email = *email* in status = *status*.
   You are not obliged to specify all the parameters but only those that you need.

   :param int list_id: id of the List in which to retrieve the recipient
   :param int recipient_id: recipient id to find
   :param str email: recipient email to find
   :param str status: status is a string in 'subscribed' 'unsubscribed' or 'pending', None for consider all
   :return: Recipient instance
   :rtype: Recipient
   :raises RecipientNotFoundException: if the recipient is not found on list with id = *list_id*
   :raises ListNotFoundException: if a list with id = *list_id* does not exists on your MailUp account
   :raises InvalidRecipientStatusException: status not in 'subscribed' 'unsubscribed' or 'pending'
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


all_subscribe_recipients
++++++++++++++++++++++++

.. py:function:: all_subscribe_recipients(list_id)

   Retrieve a instance list of all Recipient on List with id = *list_id* in 'subscribed' status

   :param int list_id: id of the List in which to retrieve the recipients
   :return: list of Recipient instance
   :rtype: list
   :raises ListNotFoundException: if a list with id = *list_id* does not exists on your MailUp account
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


all_unsubscribe_recipients
++++++++++++++++++++++++++

.. py:function:: all_unsubscribe_recipients(list_id)

   Retrieve a instance list of all Recipient on List with id = *list_id* in 'unsubscribed' status

   :param int list_id: id of the List in which to retrieve the recipients
   :return: list of Recipient instance
   :rtype: list
   :raises ListNotFoundException: if a list with id = *list_id* does not exists on your MailUp account
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


all_pending_recipients
++++++++++++++++++++++

.. py:function:: all_pending_recipients(list_id)

   Retrieve a instance list of all Recipient on List with id = *list_id* in 'pending' status

   :param int list_id: id of the List in which to retrieve the recipients
   :return: list of Recipient instance
   :rtype: list
   :raises ListNotFoundException: if a list with id = *list_id* does not exists on your MailUp account
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


all_pending_recipients
++++++++++++++++++++++

.. py:function:: all_pending_recipients(list_id)

   Retrieve a instance list of all Recipient on List with id = *list_id* in 'pending' status

   :param int list_id: id of the List in which to retrieve the recipients
   :return: list of Recipient instance
   :rtype: list
   :raises ListNotFoundException: if a list with id = *list_id* does not exists on your MailUp account
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


all_recipients
++++++++++++++

.. py:function:: all_recipients(list_id)

   Retrieve a instance list of all Recipient on List with id = *list_id* in any status

   :param int list_id: id of the List in which to retrieve the recipients
   :return: list of Recipient instance
   :rtype: list
   :raises ListNotFoundException: if a list with id = *list_id* does not exists on your MailUp account
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


filter_recipients
+++++++++++++++++

.. py:function:: filter_recipients(list_id, filters)

   Retrieve a instance list of all Recipients on List with id=list_id filtered by *filters* dict; *filters* is structured like data_dict,
   in fact you can use own *data_dict*. The '==' operator is applied (refer to
   `MailUp documentation <http://help.mailup.com/display/mailupapi/Paging+and+filtering#Pagingandfiltering-Filtering>`_ for detail.)

   :return: instance list
   :rtype: list
   :raises ListNotFoundException: if a list with id = *list_id* does not exists on your MailUp account
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


create_message
++++++++++++++

.. py:function:: create_message(message_data_dict, content='', embed=False, is_confirmation=False, tracking_info=None)

   Create a Recipient on List, List on which it is created is defined in *message_data_dict*

   :param dict message_data_dict: data dict
   :param str content: content
   :param bool embed: embed
   :param bool is_confirmation: is_confirmation
   :param dict tracking_info: tracking_info
   :return: Message instance
   :rtype: Message
   :raises InvalidMessageConfigurationException: bad data dict
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


get_message
+++++++++++

.. py:function:: get_message(list_id, message_id)

   Retrieve a Message in a List with id *list_id* instance with id = *group_id*

   :param int list_id: id of the List in which to retrieve the message
   :param int message_id: id of message to retrieve
   :return: Message instance
   :rtype: Message
   :raises MessageNotFoundException:  if a message is not found on list with id = *list_id*
   :raises ListNotFoundException: if a list with id = *list_id* does not exists on your MailUp account
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


all_messages
++++++++++++

.. py:function:: all_messages(list_id, status=None)

   Retrieve a instance list of all messages on List with id = *list_id* in status = *status*

   :param int list_id: id of the List in which to retrieve the messages
   :param str status: status is a string in 'published' or 'archived', None for consider all
   :return: list of Message instance
   :rtype: list
   :raises ListNotFoundException: if a list with id = *list_id* does not exists on your MailUp account
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


all_published_messages
++++++++++++++++++++++

.. py:function:: all_published_messages(list_id)

   Retrieve a instance list of all messages on List with id = *list_id* in 'published' status

   :param int list_id: id of the List in which to retrieve the messages
   :return: list of Message instance
   :rtype: list
   :raises ListNotFoundException: if a list with id = *list_id* does not exists on your MailUp account
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


all_archived_messages
+++++++++++++++++++++

.. py:function:: all_archived_messages(list_id)

   Retrieve a instance list of all messages on List with id = *list_id* in 'archived' status

   :param int list_id: id of the List in which to retrieve the messages
   :return: list of Message instance
   :rtype: list
   :raises ListNotFoundException: if a list with id = *list_id* does not exists on your MailUp account
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


filter_messages
+++++++++++++++

.. py:function:: filter_messages(list_id, filters)

   Retrieve a instance list of all Messages on List with id=list_id filtered by *filters* dict; *filters* is structured like data_dict,
   in fact you can use own *data_dict*. The '==' operator is applied (refer to
   `MailUp documentation <http://help.mailup.com/display/mailupapi/Paging+and+filtering#Pagingandfiltering-Filtering>`_ for detail.)

   :return: instance list
   :rtype: list
   :raises ListNotFoundException: if a list with id = *list_id* does not exists on your MailUp account
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


create_tag
++++++++++

.. py:function:: create_tag(data_dict)

   Create a Tag on List, List on which it is created is defined in *data_dict*

   :param dict data_dict: data dict
   :return: Tag instance
   :rtype: Tag
   :raises InvalidTagConfigurationException: bad data dict
   :raises TagAlreadyExistException: tag with data_dict['name'] already exists
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


get_tag
+++++++

.. py:function:: get_tag(tag_id=None, tag_name=None)

   Retrieve a Tag instance with id = *tag_id* and name = *email* in a List with id *list_id* .
   You are not obliged to specify all the parameters but only those that you need.

   :param int tag_id: tag id to find
   :param str tag_name: tag name to find
   :return: Tag instance
   :rtype: Tag
   :raises TagNotFoundException: if the tag is not found on list with id = *list_id*
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


all_tags
++++++++

.. py:function:: all_tags(list_id)

   Retrieve a instance list of all tags on List with id = *list_id*

   :param int list_id: id of the List in which to retrieve the tags
   :return: list of Tag instance
   :rtype: list
   :raises ListNotFoundException: if a list with id = *list_id* does not exists on your MailUp account
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


all_attachments
+++++++++++++++

.. py:function:: all_attachments(list_id, message_id)

   Retrieve a instance list of all attachments of message with id = *message_id*

   :param int list_id: id of the List in which to retrieve the attachments
   :param int message_id: id of the Message to which are attached
   :return: list of Attachments instance
   :rtype: list
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MessageNotFoundException: message_id not exists
   :raises ListNotFoundException: if a list with id = *list_id* does not exists on your MailUp account
   :raises MailUpCallError: Error calling the API


get_attachments
+++++++++++++++

.. py:function:: get_attachments(list_id, message_id, file_name=None, slot=None)

   Retrieve a instance list of all attachments of message with id = *message_id*. If *file_name* and *slot* are passed
   attachments are filtered

   :param int list_id: id of the List in which to retrieve the attachments
   :param int message_id: id of the Message to which are attached
   :param int file_name: name of file to filter
   :param int slot: slot of file to filter. slut must be >= 1 and <= 5
   :return: list of Attachments instance
   :rtype: list
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MessageNotFoundException: message_id not exists
   :raises ListNotFoundException: if a list with id = *list_id* does not exists on your MailUp account
   :raises MailUpCallError: Error calling the API


