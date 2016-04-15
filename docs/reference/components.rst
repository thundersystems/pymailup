Components
==========


Once you instantiate an object of type List, Group, Recipient, etc.. you can use the following methods provided by the
relative class.
All components have some common behaviors:

       :id: property to get/set id of component
       :save: method to save component changes on MailUp (see below for detail)
       :client: MailUpClient instance used to call MailUp API
       :logger: logger
       :data_dict: internal dictionary related to received json
       :mailup_pattern_fields: dictionary where the keys are which fields of json must be configured as component attributes
                               and values the names that you want give to them
       :required_fields: list of required items in *data_dict*
       :get_list method: method that return List in which is located the component, if component is a List return himself

List
++++

save
----


.. py:function:: save()

   Save the List on MailUp platform. If the object as no *id* then a new object is created on MailUp.

   :return: List Instance
   :rtype: List or Group or Recipient or Message or Tag based on caller instance.
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


get_groups
----------

.. py:function:: get_groups()

   Retrieve all groups in list

   :return: list of Group instance
   :rtype: list
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


get_recipients
--------------

.. py:function:: get_recipients(status=None)

   Retrieve all recipients in list. If *status* is None all recipients are returned regardless of the status

   :param str status: status is a string in 'subscribed' 'unsubscribed' or 'pending', None for consider all
   :return: list of Recipient instance
   :rtype: list
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


get_subscribers
---------------

.. py:function:: get_subscribers()

   Retrieve all recipients in *subscribed* status in list

   :return: list of Recipient instance
   :rtype: list
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


get_unsubscribers
-----------------

.. py:function:: get_unsubscribers()

   Retrieve all recipients in *unsubscribed* status in list

   :return: list of Recipient instance
   :rtype: list
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


get_pending
-----------

.. py:function:: get_pending()

   Retrieve all recipients in *pending* status in List

   :return: list of Recipient instance
   :rtype: list
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API



subscribe_recipients_list
-------------------------

.. py:function:: subscribe_recipients_list(recipients, confirm_email=False, wait_import=False)

   Subscribe all recipient in *recipients* in List

   :param list recipients: list of Recipient instance
   :param bool confirm_email: refer to `MailUp documentation <http://help.mailup.com/display/mailupapi/Recipients#Recipients-Manageasingleemailrecipient/subscriber>`_
   :param bool wait_import: method ends only when import is complete
   :return: import_id
   :rtype: int
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


subscribe_recipients_list_forced
--------------------------------

.. py:function:: subscribe_recipients_list_forced(recipients, confirm_email=False, wait_import=False)

   Subscribe all recipient in *recipients* in list, are subscribe both pending the unsubscribed

   :param list recipients: list of Recipient instance
   :param bool confirm_email: refer to `MailUp documentation <http://help.mailup.com/display/mailupapi/Recipients#Recipients-Manageasingleemailrecipient/subscriber>`_
   :param bool wait_import: method ends only when import is complete
   :return: import_id
   :rtype: int
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


unsubscribe_recipients_list
---------------------------

.. py:function:: unsubscribe_recipients_list(recipients, wait_import=False)

   Unsubscribe all recipient in *recipients* from List

   :param list recipients: list of Recipient instance
   :param bool wait_import: method ends only when import is complete
   :return: import_id
   :rtype: int
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


send_confirmation_email
-----------------------

.. py:function:: send_confirmation_email(import_id, send_date=None)

   A confirmation email is sent at all recipient subscribed in *import_id* import.

   :param int import_id: id of import (see unsubscribe_recipients_list)
   :param datetime send_date: datetime to send message, None to send instantly.
   :return: sending info and statistic
   :rtype: dict
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


get_import_status
-----------------

.. py:function:: get_import_status(import_id)

   Retrieve status of import *import_id*. If *import_id* is not valid *None* is returned from MailUp and then from this methods.

   :param int import_id: id of import to retrieve status
   :return: import statistics
   :rtype: dict
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


Group
+++++

save
----


.. py:function:: save()

   Save the Group on MailUp platform. If the object as no *id* then a new object is created on MailUp.

   :return: Group Instance
   :rtype: List or Group or Recipient or Message or Tag based on caller instance.
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


delete
------

.. py:function:: delete()

   Delete instantly the group on MailUp

   :return: None
   :rtype: None
   :raises GroupNotFoundException: group (searched by id) not found
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API

get_subscribers
---------------

.. py:function:: get_subscribers()

   Retrieve all recipients in *subscribed* status in group

   :return: list of Recipient instance
   :rtype: list
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API



insert_recipient
----------------

.. py:function:: insert_recipient(recipient_id)

   Insert recipient with id = *recipient_id* in group

   :param int recipient_id: id of recipient to insert
   :return: None
   :rtype: None
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


extract_recipient
-----------------

.. py:function:: extract_recipient(recipient_id)

   Extract recipient with id = *recipient_id* from group

   :param int recipient_id: id of recipient to extract
   :return: None
   :rtype: None
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


subscribe_recipients_list
-------------------------

.. py:function:: subscribe_recipients_list(recipients, confirm_email=False, wait_import=False)

   Subscribe all recipient in *recipients* in group

   :param list recipients: list of Recipient instance
   :param bool confirm_email: refer to `MailUp documentation <http://help.mailup.com/display/mailupapi/Recipients#Recipients-Manageasingleemailrecipient/subscriber>`_
   :param bool wait_import: method ends only when import is complete
   :return: import_id
   :rtype: int
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


subscribe_recipients_list_forced
--------------------------------

.. py:function:: subscribe_recipients_list_forced(recipients, confirm_email=False, wait_import=False)

   Subscribe all recipient in *recipients* in group, are subscribe both pending the unsubscribed

   :param list recipients: list of Recipient instance
   :param bool confirm_email: refer to `MailUp documentation <http://help.mailup.com/display/mailupapi/Recipients#Recipients-Manageasingleemailrecipient/subscriber>`_
   :param bool wait_import: method ends only when import is complete
   :return: import_id
   :rtype: int
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


unsubscribe_recipients_list
---------------------------

.. py:function:: unsubscribe_recipients_list(recipients, wait_import=False)

   Unsubscribe all recipient in *recipients* from group

   :param list recipients: list of Recipient instance
   :param bool wait_import: method ends only when import is complete
   :return: import_id
   :rtype: int
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


send_confirmation_email
-----------------------

.. py:function:: send_confirmation_email(import_id, send_date=None)

   A confirmation email is sent at all recipient subscribed in *import_id* import.

   :param int import_id: id of import (see unsubscribe_recipients_list)
   :param datetime send_date: datetime to send message, None to send instantly.
   :return: sending info and statistic
   :rtype: dict
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


send_message
------------

.. py:function:: send_message(message_id)

   Message *message_id* is sent to group

   :param int message_id: id of message to send
   :return: sending info and statistic
   :rtype: dict
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API



Recipient
+++++++++

save
----

.. py:function:: save()

   Save the Recipient on MailUp platform. If the object as no *id* then a new object is created on MailUp.

   :return: Recipient Instance
   :rtype: List or Group or Recipient or Message or Tag based on caller instance.
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


add_to_list
-----------

.. py:function:: add_to_list(list_id, confirm_email=False)

   Add a recipient in list

   :param int list_id: id of the list in which to insert the recipient
   :param bool confirm_email: refer to `MailUp documentation <http://help.mailup.com/display/mailupapi/Recipients#Recipients-Addasinglerecipient/subscriber(synchronousimport)>`_
   :return: Recipient instance
   :rtype: Recipient
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


subscribe_to_list
-----------------

.. py:function:: subscribe_to_list(list_id)

   Subscribe a recipient in list

   :param int list_id: id of the list in which to subscribe the recipient
   :return: Recipient instance
   :rtype: Recipient
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


unsubscribe_to_list
-------------------

.. py:function:: unsubscribe_to_list(list_id)

   Unsubscribe a recipient in list

   :param int list_id: id of the list in which to unsubscribe the recipient
   :return: Recipient instance
   :rtype: Recipient
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


add_to_group
------------

.. py:function:: add_to_group(group_id, confirm_email=False)

   Add a recipient in a group

   :param int group_id: id of the group in which to unsubscribe the recipient
   :param bool confirm_email: refer to `MailUp documentation <http://help.mailup.com/display/mailupapi/Recipients#Recipients-Addasinglerecipient/subscriber(synchronousimport)>`_
   :return: Recipient instance
   :rtype: Recipient
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


set_field
---------

.. py:function:: set_field(field_name, field_value)

   Set a recipient field, save() method is necessary to align MailUp platform

   :param str field_name: name of field to set
   :param str field_value: value to be assigned to the field
   :return: None
   :rtype: None


get_field
---------

.. py:function:: get_field(field_name)

   Get the value of field_name

   :param str field_name: name of field to get
   :return: value of field
   :rtype: str


set_fields
----------

.. py:function:: set_fields(field_dict)

   Set a recipient fields through a dictionary where the keys are fields name and the values are the fields values,
   save() method is necessary to align MailUp platform.

   :param dict field_dict: dict of fields
   :return: None
   :rtype: None


get_fields
----------

.. py:function:: get_fields()

   Get a dictionary of fields where the keys are fields name and the values are the fields values

   :return: dictionary of fields
   :rtype: dict


Message
+++++++

save
----

.. py:function:: save()

   Save the Message on MailUp platform. If the object as no *id* then a new object is created on MailUp.

   :return: Message Instance
   :rtype: List or Group or Recipient or Message or Tag based on caller instance.
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


send_to_list
------------

.. py:function:: send_to_list(list_id)

   Send message to list

   :param int list_id: id of the list to which to send the message
   :return: sending info and statistic
   :rtype: dict
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


send_to_group
-------------

.. py:function:: send_to_group(group_id)

   Send message to group

   :param int group_id: id of the group to which to send the message
   :return: sending info and statistic
   :rtype: dict
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


send_to_recipient
-----------------

.. py:function:: send_to_recipient(recipient_id)

   Send message to recipient

   :param int group_id: id of the recipient to which to send the message
   :return: sending info and statistic
   :rtype: dict
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API


set_field
---------

.. py:function:: set_field(field_name, field_value)

   Set a recipient field, save() method is necessary to align MailUp platform

   :param str field_name: name of field to set
   :param str field_value: value to be assigned to the field
   :return: None
   :rtype: None


get_field
---------

.. py:function:: get_field(field_name)

   Get the value of field_name

   :param str field_name: name of field to get
   :return: value of field
   :rtype: str


Tag
+++


save
----

.. py:function:: save()

   Save the Tag on MailUp platform. If the object as no *id* then a new object is created on MailUp.

   :return: Tag Instance
   :rtype: List or Group or Recipient or Message or Tag based on caller instance.
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API



Attachment
++++++++++

save
----

.. py:function:: save()

   Save the Attachment on MailUp platform. If the object as no *id* then a new object is created on MailUp.

   :return: Attachment Instance
   :rtype: List or Group or Recipient or Message or Tag based on caller instance.
   :raises ClientNotEnabledException: provider as not a client configured
   :raises MailUpCallError: Error calling the API
