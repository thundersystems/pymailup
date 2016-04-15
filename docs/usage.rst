=====
Usage
=====

First step to use pymailup in a project is import it::

	import mailup

To create or retrieve objects from MailUp you must instantiate a *provider* which itself uses a *client* instance.
Below the steps to create a client and a provider.

To build a client you need the credentials obtained from your MailUp account: "CLIENT_ID", "CLIENT_SECRET", "USERNAME" and "PASSWORD"::

    from mailup.object_providers import MailUpObjectProvider
    from mailup.clients import MailUpClientSingleton

    # client
    mailup_client = MailUpClientSingleton(
        client_id='CLIENT_ID',
        client_secret='CLIENT_SECRET',
        username='USERNAME',
        password='PASSWORD',
    )

    # provider
    provider = MailUpObjectProvider(client=mailup_client)



In this Example a *Singleton* class is used. You are free to use *MailUpClient* but singleton class is recommended
if you intend to use a single account.

Now that you have the *provider* can proceed with  *get* / *all* / *create* / *filters* operations explained in the following paragraphs.

Next basic example shown how to change the name of a list on MailUp platform::

    # get list with id = 1
    list1 = provider.get_list(1)

    # rename local instance
    list1.name = 'new name of list1'

    # save local changes on MailUp
    list1.save()

In this case we have only changed the name to a list, but once you have the object instance (*list1* in the example) there
are many methods you can use. Please refer to the following paragraphs a complete description of all methods.
