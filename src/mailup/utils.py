# coding: utf-8

from mailup import exceptions
from mailup.providers import MailUpComponentProvider


# CLIENT
def filters_to_querystring(filters):
    """
    Transform a dictionary in querystring: ES. "Name==John&LastName=='Doe'"
    :param filters: dictionary
    :return:
    """
    filters = filters or dict()
    params = dict()
    filters_string = ''
    for p_name, p_value in filters.iteritems():
        filter_string = "{p_name}=='{p_value}'&".format(
            p_name=p_name,
            p_value=p_value,
        )
        if type(p_value) == int:
            filter_string = filter_string.replace("'", "")

        filters_string = filters_string + filter_string

    if filters_string:
        filters_string = filters_string[:-1]
        params = {
            "filterby": filters_string,
        }
    return params


# ALL COMPONENTS
def filter_dict(original_dict, pattern_dict):
    """
    Return a dict that contains all items of original_dict if item key is in pattern_dict.keys()
    :param original_dict:
    :param pattern_dict:
    :return:
    """
    keys = set(original_dict.keys()).intersection(pattern_dict.keys())
    return {key: original_dict[key] for key in keys}


def check_object_exist(obj, client):
    obj_name = obj.__class__.__name__.lower()
    method_kwargs = {}

    if not obj_name == 'list':
        # all components except list need to have list_id in provider.get_ method
        try:
            method_kwargs['list_id'] = obj.data_dict['idList']
        except KeyError:
            raise exceptions.ListNotSpecifiedException()

    obj_pk_name = '{}_id'.format(obj_name)
    method_kwargs[obj_pk_name] = obj.id

    method_name = 'get_{}'.format(obj_name)

    provider = MailUpComponentProvider(client=client)

    # calling provider.get_ method NotFoundException has rise
    getattr(provider, method_name)(**method_kwargs)


