# coding: utf-8

import base64
import json
import requests
import time

from mailup import exceptions
from mailup import utils
from mailup.logger import LoggerSingleton

# MAILUP CONFIGURATION FILE
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
    'MAILUP_CLIENT_TIMEOUT': 60,
    'MAILUP_CLIENT_TIMEOUT_403': 60,
    'MAILUP_CLIENT_ATTEMPT_WAIT': 2,
}


class MailUpClient(object):

    # MAILUP LOGGER SINGLETON
    logger = None

    # MAILUP CONFIGURATION
    configuration_dict = _initial_client_configuration

    def __init__(self, client_id, client_secret, username, password, logger_enabled=False):
        # Init Logger
        self.logger = LoggerSingleton()
        if not logger_enabled:
            self.logger.disabled = True

        self.configuration['MAILUP_CLIENT_ID'] = client_id
        self.configuration['MAILUP_CLIENT_SECRET'] = client_secret
        self.configuration['MAILUP_USERNAME'] = username
        self.configuration['MAILUP_PASSWORD'] = password

        self.access_token = None
        self.refreshed_token = None
        self.retrieve_access_token()

    @property
    def configuration(self):
        return self.configuration_dict

    @configuration.setter
    def configuration(self, configuration_dict):
        self.configuration_dict = configuration_dict

    @property
    def logon_endpoint(self):
        return self.configuration['MAILUP_END_POINTS']['LOGON_END_POINT']

    @logon_endpoint.setter
    def logon_endpoint(self, value):
        self.configuration['MAILUP_END_POINTS']['LOGON_END_POINT'] = value

    @property
    def authorization_endpoint(self):
        return self.configuration['MAILUP_END_POINTS']['AUTHORIZATION_END_POINT']

    @authorization_endpoint.setter
    def authorization_endpoint(self, value):
        self.configuration['MAILUP_END_POINTS']['AUTHORIZATION_END_POINT'] = value

    @property
    def token_endpoint(self):
        return self.configuration['MAILUP_END_POINTS']['TOKEN_END_POINT']

    @token_endpoint.setter
    def token_endpoint(self, value):
        self.configuration['MAILUP_END_POINTS']['TOKEN_END_POINT'] = value

    @property
    def console_endpoint(self):
        return self.configuration['MAILUP_END_POINTS']['CONSOLE_END_POINT']

    @console_endpoint.setter
    def console_endpoint(self, value):
        self.configuration['MAILUP_END_POINTS']['CONSOLE_END_POINT'] = value

    @property
    def mail_statistics_endpoint(self):
        return self.configuration['MAILUP_END_POINTS']['MAIL_STATISTICS_END_POINT']

    @mail_statistics_endpoint.setter
    def mail_statistics_endpoint(self, value):
        self.configuration['MAILUP_END_POINTS']['MAIL_STATISTICS_END_POINT'] = value

    @property
    def send_mail_endpoint(self):
        return self.configuration['MAILUP_END_POINTS']['SEND_MESSAGE_END_POINT']

    @send_mail_endpoint.setter
    def send_mail_endpoint(self, value):
        self.configuration['MAILUP_END_POINTS']['SEND_MESSAGE_END_POINT'] = value

    @property
    def client_id(self):
        return self.configuration['MAILUP_CLIENT_ID']

    @client_id.setter
    def client_id(self, value):
        self.configuration['MAILUP_CLIENT_ID'] = value

    @property
    def client_secret(self):
        return self.configuration['MAILUP_CLIENT_SECRET']

    @client_secret.setter
    def client_secret(self, value):
        self.configuration['MAILUP_CLIENT_SECRET'] = value

    # SUPPORT METHODS
    def get_headers(self):
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer {access_token}".format(
                access_token=self.access_token
            ),
        }

    def call_handler(
        self, method, url, data=None, params=None, headers=None, cookies=None, attempts=None, timeout=None,
        page_size=None, page_number=0,
    ):
        attempts = attempts or self.configuration_dict['MAILUP_CLIENT_ATTEMPTS']
        timeout = timeout or self.configuration_dict['MAILUP_CLIENT_TIMEOUT']
        page_size = page_size or self.configuration_dict['MAILUP_DEFAULT_PAGE_SIZE']


        # PARAMS FOR RESPONSE LIB
        if params is None:
            params = {}
        params["PageNumber"] = page_number
        params["PageSize"] = page_size

        mailup_response = None

        # CALL
        while attempts > 0:
            try:
                self.logger.debug("""Calling url "{url}" in {method} with:
                data = {data}
                params = {params}
                headers = {headers}
                cookies = {cookies}""".format(
                    method=method.upper(),
                    url=url,
                    data=data,
                    params=params,
                    headers=headers,
                    cookies=cookies
                ))
                response = self.do_call(
                    method, url, data=data, params=params, headers=headers, cookies=cookies,
                    timeout=timeout, attempts=attempts
                )
            except exceptions.MailUpCallError:
                self.logger.critical("MailUp does not respond")
                break

            self.logger.debug('HTTP response: {response}'.format(response=response))

            # 200: success
            if response.status_code == 200:
                if not response.content:
                    # Any API like delete group return None if OK
                    return None
                r_json = response.json()
                if not mailup_response:
                    mailup_response = r_json
                else:
                    if 'Items' in r_json and len(r_json['Items']):
                        mailup_response['Items'] = mailup_response.get('Items', []) + r_json.get('Items', [])
                    else:
                        break
                try:
                    if type(mailup_response) is dict:
                        if 'Items' in mailup_response and type(mailup_response['Items']) is list and len(mailup_response['Items']):
                            params["PageNumber"] += 1
                            continue
                        else:
                            break
                    else:
                        break
                except TypeError:
                    break

            # 401: unauthorised
            elif response.status_code == 401:
                self.logger.error('Response status 401')
                self.refresh_token()
                headers = self.get_headers()
                # if "Authorization" in headers and headers["Authorization"].startswith("Bearer"):
                #     headers["Authorization"] = "Bearer {access_token}".format(
                #         access_token=self.access_token
                #     )

            elif response.status_code == 403:
                self.logger.error('Response status 403: {}'.format(response.content))
                self.logger.error('waiting {} seconds. You probably have just created a list and MailUp is not ready yet'.format(
                    self.configuration_dict['MAILUP_CLIENT_TIMEOUT_403'])
                )
                time.sleep(self.configuration_dict['MAILUP_CLIENT_TIMEOUT_403'])

            elif response.status_code == 404:
                self.logger.error('Response status 404')
                break

            elif response.status_code == 500:
                self.logger.error('HTTP request error: {}'.format(response.reason))
                break
            else:
                # Other error
                error_message = response.text.replace('\\\'', '"').replace('\'', '"')
                self.logger.error('HTTP request error: {}'.format(error_message))
                break

            attempts -= 1
            self.logger.warning('Attempts remaining: {attempts}/{tot_attempt}'.format(
                attempts=attempts,
                tot_attempt=self.configuration_dict['MAILUP_CLIENT_ATTEMPTS']
            ))

        return mailup_response

    def do_call(
        self, method, url, data=None, params=None, headers=None, cookies=None, attempts=1,
        timeout=None
    ):
        timeout = timeout or self.configuration_dict['MAILUP_CLIENT_ATTEMPT_WAIT']
        for i in range(0, attempts):
            try:
                response = getattr(requests, method.lower())(
                    url, data=data, params=params, headers=headers, cookies=cookies,
                    timeout=self.configuration_dict['MAILUP_CLIENT_TIMEOUT']
                )
                return response
            except requests.exceptions.Timeout:
                self.logger.error(
                    'ERROR during attempt {}/{}: MailUpRequest Timeout'.format(i+1, attempts)
                )
                if i != attempts:
                    self.logger.error(
                        'Recalling API after {} seconds'.format(self.configuration_dict['MAILUP_CLIENT_ATTEMPT_WAIT'])
                    )
                time.sleep(self.configuration_dict['MAILUP_CLIENT_ATTEMPT_WAIT'])
        raise exceptions.MailUpCallError('Max attempts exceeded')

    def retrieve_access_token(self):
        """
        Use credential settings to initialize "accessToken" and "refreshToken"
        """
        self.logger.debug('Retrieving access token...')
        url = self.token_endpoint
        params = {
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": self.configuration['MAILUP_USERNAME'],
            "password": self.configuration['MAILUP_PASSWORD'],
        }
        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'Authorization': "Basic {access_token}".format(
                access_token=base64.b64encode(self.client_id+":"+self.client_secret),
            )
        }
        rest_request_json = self.call_handler("POST", url, params=params, headers=headers)
        self.access_token = rest_request_json["access_token"]
        self.refreshed_token = rest_request_json["refresh_token"]
        self.logger.debug('Access token retrieved')

    def refresh_token(self):
        """
        Refresh "accessToken" and "refreshToken"
        """
        self.logger.debug('Refreshing token...')
        url = self.token_endpoint
        params = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refreshed_token,
        }
        headers = {
            'content-type': 'application/x-www-form-urlencoded',
        }
        rest_request_json = self.call_handler("POST", url, params=params, headers=headers)
        self.access_token = rest_request_json["access_token"]
        self.refreshed_token = rest_request_json["refresh_token"]
        self.logger.debug('Token refreshed')

    def read_authentication_info(self, **kwargs):
        """
        Get authentication info from MailUp
        :return: a json like:
        {
            u'Username': u'm78078',
            u'Company': u'Thunder Systems',
            u'IsTrial': False,
            u'Version': u'8.9.0',
            u'UID': u'41446'
        }
        """
        url = self.console_endpoint + "/Console/Authentication/Info"
        headers = {
            "Authorization": "Bearer {access_token}".format(
                access_token=self.access_token
            )
        }
        return self.call_handler("GET", url, headers=headers, **kwargs)

    def get_account_details(self, **kwargs):
        url = self.console_endpoint + "/Console/Authentication/Info"
        call_response = self.call_handler(
            "GET", url, headers=self.get_headers(), **kwargs
        )
        return call_response

    # LIST
    def create_list(self, data_dict, **kwargs):
        url = self.console_endpoint + "/Console/User/Lists"
        call_response = self.call_handler(
            "POST", url, data=json.dumps(data_dict), headers=self.get_headers(), **kwargs
        )
        return call_response

    def update_list(self, data_dict, **kwargs):
        list_id = data_dict['IdList']
        url = self.console_endpoint + "/Console/User/List/{list_id}".format(list_id=list_id)
        call_response = self.call_handler(
            "PUT", url, data=json.dumps(data_dict), headers=self.get_headers(), **kwargs
        )
        return call_response

    def read_lists(self, filters=None, **kwargs):
        url = self.console_endpoint + "/Console/User/Lists"
        params = utils.filters_to_querystring(filters)
        call_response = self.call_handler("GET", url, params=params, headers=self.get_headers(), **kwargs)
        return call_response

    # GROUP
    def create_group(self, list_id, data_dict, **kwargs):
        """
        Create group in list "list_id" with name "group_name"

        :param list_id:
        :return: group_id
        """
        url = self.console_endpoint + "/Console/List/{list_id}/Group".format(
            list_id=list_id,
        )
        call_response = self.call_handler(
            "POST", url, data=json.dumps(data_dict), headers=self.get_headers(), **kwargs
        )
        return call_response

    def update_group(self, list_id, group_id, data_dict, **kwargs):
        url = self.console_endpoint + "/Console/List/{list_id}/Group/{group_id}".format(
            list_id=list_id,
            group_id=group_id,
        )
        call_response = self.call_handler(
            "PUT", url, data=json.dumps(data_dict), headers=self.get_headers(), **kwargs
        )
        return call_response

    def read_groups(self, list_id, filters=None, **kwargs):
        url = self.console_endpoint + "/Console/List/{list_id}/Groups".format(
            list_id=list_id,
        )
        params = utils.filters_to_querystring(filters)
        call_response = self.call_handler("GET", url, params=params, headers=self.get_headers(), **kwargs)
        return call_response

    def delete_group(self, list_id, group_id, **kwargs):
        url = self.console_endpoint + "/Console/List/{list_id}/Group/{group_id}".format(
            list_id=list_id,
            group_id=group_id,
        )
        call_response = self.call_handler("DELETE", url, headers=self.get_headers(), **kwargs)
        return call_response

    # RECIPIENT
    def add_recipient_to_list(self, list_id, data_dict, confirm_email=False, **kwargs):
        url = self.console_endpoint + "/Console/List/{list_id}/Recipient?ConfirmEmail={confirm_email}".format(
            list_id=list_id,
            confirm_email=confirm_email,
        )
        call_response = self.call_handler(
            "POST", url, data=json.dumps(data_dict), headers=self.get_headers(), **kwargs
        )
        if not call_response:
            raise exceptions.InvalidRecipientConfigurationException(data_dict)
        return call_response

    def add_recipient_to_group(self, group_id, data_dict, confirm_email=False, **kwargs):
        url = self.console_endpoint + "/Console/Group/{group_id}/Recipient?ConfirmEmail={confirm_email}".format(
            group_id=group_id,
            confirm_email=confirm_email,
        )
        call_response = self.call_handler(
            "POST", url, data=json.dumps(data_dict), headers=self.get_headers(), **kwargs
        )
        return call_response

    def update_recipient(self, data_dict, **kwargs):
        url = self.console_endpoint + "/Console/Recipient/Detail"
        call_response = self.call_handler(
            "PUT", url, data=json.dumps(data_dict), headers=self.get_headers(), **kwargs
        )
        return call_response

    def subscribe_recipient_to_list(self, list_id, recipient_id, **kwargs):
        url = self.console_endpoint + "/Console/List/{list_id}/Subscribe/{recipient_id}".format(
            list_id=list_id,
            recipient_id=recipient_id,
        )
        call_response = self.call_handler("POST", url, headers=self.get_headers(), **kwargs)
        return call_response

    def unsubscribe_recipient_to_list(self, list_id, recipient_id, **kwargs):
        url = self.console_endpoint + "/Console/List/{list_id}/Unsubscribe/{recipient_id}".format(
            list_id=list_id,
            recipient_id=recipient_id,
        )
        call_response = self.call_handler("DELETE", url, headers=self.get_headers(), **kwargs)
        return call_response

    def update_list_unsubscription(self, list_id, recipient_id, **kwargs):
        url = self.console_endpoint + "/Console/List/{list_id}/Unsubscribe/{recipient_id}".format(
            list_id=list_id,
            recipient_id=recipient_id,
        )
        call_response = self.call_handler("DELETE", url, headers=self.get_headers(), **kwargs)
        return call_response

    def update_group_subscription(self, group_id, recipient_id, **kwargs):
        url = self.console_endpoint + "/Console/Group/{group_id}/Subscribe/{recipient_id}".format(
            group_id=group_id,
            recipient_id=recipient_id,
        )
        call_response = self.call_handler("POST", url, headers=self.get_headers(), **kwargs)
        return call_response

    def update_group_unsubscription(self, group_id, recipient_id, **kwargs):
        url = self.console_endpoint + "/Console/Group/{group_id}/Unsubscribe/{recipient_id}".format(
            group_id=group_id,
            recipient_id=recipient_id,
        )
        call_response = self.call_handler("DELETE", url, headers=self.get_headers(), **kwargs)
        return call_response

    def subscribe_recipients_to_list(
        self, list_id, list_data_dict, confirm_email=False, import_type=None, **kwargs
    ):
        """
        :param list_id:
        :param list_data_dict:
        :param confirm_email: ConfirmEmail=true: if specified, sets the new recipients status to "Pending", and a
               confirmation email is generated (but not yet sent).
        :return:
        """
        url = self.console_endpoint + "/Console/List/{list_id}/Recipients?ConfirmEmail={confirm_email}".format(
            list_id=list_id,
            confirm_email=confirm_email,
        )
        if import_type:
            params = {"importType": import_type}
        else:
            params = {}
        call_response = self.call_handler(
            "POST", url, data=json.dumps(list_data_dict), headers=self.get_headers(), params=params, **kwargs
        )
        return call_response

    def unsubscribe_recipients_to_list(self, list_id, list_data_dict, import_type='asOptout', **kwargs):
        url = self.console_endpoint + "/Console/List/{list_id}/Recipients?importType={import_type}".format(
            list_id=list_id,
            import_type=import_type,
        )
        call_response = self.call_handler(
            "POST", url, data=json.dumps(list_data_dict), headers=self.get_headers(), **kwargs
        )
        return call_response

    def subscribe_recipients_to_group(
        self, group_id, list_data_dict, confirm_email=False, import_type=None, **kwargs
    ):
        url = self.console_endpoint + "/Console/Group/{group_id}/Recipients?ConfirmEmail={confirm_email}".format(
            group_id=group_id,
            confirm_email=confirm_email,
        )
        if import_type:
            params = {"importType": import_type}
        else:
            params = {}
        call_response = self.call_handler(
            "POST", url, data=json.dumps(list_data_dict), headers=self.get_headers(), params=params, **kwargs
        )
        return call_response

    def unsubscribe_recipients_to_group(self, group_id, list_data_dict, import_type='asOptout', **kwargs):
        url = self.console_endpoint + "/Console/Group/{group_id}/Recipients?importType={import_type}".format(
            group_id=group_id,
            import_type=import_type,
        )
        call_response = self.call_handler(
            "POST", url, data=json.dumps(list_data_dict), headers=self.get_headers(), **kwargs
        )
        return call_response

    def get_recipient_dynamic_field(self, **kwargs):
        url = self.console_endpoint + "/Console/Recipient/DynamicFields"
        call_response = self.call_handler("GET", url, headers=self.get_headers(), **kwargs)
        return call_response

    def get_recipients(self, list_id, status, filters=None, **kwargs):
        filters = filters or dict()
        url = None
        if status.lower() == 'subscribed':
            url = self.console_endpoint + "/Console/List/{list_id}/Recipients/Subscribed".format(
                list_id=list_id,
            )
        if status.lower() == 'unsubscribed':
            url = self.console_endpoint + "/Console/List/{list_id}/Recipients/Unsubscribed".format(
                list_id=list_id,
            )
        if status.lower() == 'pending':
            url = self.console_endpoint + "/Console/List/{list_id}/Recipients/Pending".format(
                list_id=list_id,
            )
        if not url:
            raise exceptions.InvalidRecipientStatusException(status)
        params = utils.filters_to_querystring(filters)
        call_response = self.call_handler("GET", url, params=params, headers=self.get_headers(), **kwargs)
        return call_response

    def get_subscribe_recipients_to_list(self, list_id, recipient_id=None, email=None, **kwargs):
        self.logger.warning('Client method "get_subscribe_recipients_to_list" is deprecated, use get_recipients')
        url = self.console_endpoint + "/Console/List/{list_id}/Recipients/Subscribed".format(
            list_id=list_id,
        )
        params = None
        filter_string = ''
        if recipient_id:
            filter_string = "idRecipient=={recipient_id}".format(recipient_id=recipient_id)
            if email:
                filter_string += '&'
        if email:
            filter_string += "Email=='{email}'".format(
                email=email,
            )
        if filter_string:
            params = {
                "filterby": filter_string,
            }

        call_response = self.call_handler("GET", url, params=params, headers=self.get_headers(), **kwargs)
        return call_response

    def get_unsubscribe_recipients_to_list(self, list_id, recipient_id=None, email=None, **kwargs):
        self.logger.warning('Client method "get_subscribe_recipients_to_list" is deprecated, use get_recipients')
        url = self.console_endpoint + "/Console/List/{list_id}/Recipients/Unsubscribed".format(
            list_id=list_id,
        )
        params = None
        filter_string = ''
        if recipient_id:
            filter_string = "idRecipient=={recipient_id}".format(recipient_id=recipient_id)
            if email:
                filter_string += '&'
        if email:
            filter_string += "Email=='{email}'".format(
                email=email,
            )
        if filter_string:
            params = {
                "filterby": filter_string,
            }
        call_response = self.call_handler("GET", url, headers=self.get_headers(), params=params, **kwargs)
        return call_response

    def get_pending_recipients_to_list(self, list_id, recipient_id=None, email=None, **kwargs):
        self.logger.warning('Client method "get_subscribe_recipients_to_list" is deprecated, use get_recipients')
        url = self.console_endpoint + "/Console/List/{list_id}/Recipients/Pending".format(
            list_id=list_id,
        )
        params = None
        filter_string = ''
        if recipient_id:
            filter_string = "idRecipient=={recipient_id}".format(recipient_id=recipient_id)
            if email:
                filter_string += '&'
        if email:
            filter_string += "Email=='{email}'".format(
                email=email,
            )
        if filter_string:
            params = {
                "filterby": filter_string,
            }
        call_response = self.call_handler("GET", url, headers=self.get_headers(), params=params, **kwargs)
        return call_response

    def get_belong_recipients_to_group(self, group_id, **kwargs):
        url = self.console_endpoint + "/Console/Group/{group_id}/Recipients".format(
            group_id=group_id,
        )
        call_response = self.call_handler("GET", url, headers=self.get_headers(), **kwargs)
        return call_response

    # IMPORT
    def read_import_status(self, import_id, **kwargs):
        url = self.console_endpoint + "/Console/Import/{import_id}".format(
            import_id=import_id,
        )
        call_response = self.call_handler("GET", url, headers=self.get_headers(), **kwargs)
        return call_response

    def prepare_to_send_import(self, import_id, **kwargs):
        url = self.console_endpoint + "/Console/Import/{import_id}/Sending".format(
            import_id=import_id,
        )
        call_response = self.call_handler("GET", url, headers=self.get_headers(), **kwargs)
        return call_response

    def send_import_sending(self, sending_id, send_date=None, **kwargs):
        data = dict()
        if send_date:
            data.update({'Date': '{0:%Y-%m-%d %H:%M:%S}'.format(send_date)})
            url = self.console_endpoint + "/Console/Email/Sendings/{sending_id}/Deferred".format(
                sending_id=sending_id,
            )
        else:
            url = self.console_endpoint + "/Console/Email/Sendings/{sending_id}/Immediate".format(
                sending_id=sending_id,
            )
        call_response = self.call_handler(
            "POST", url, headers=self.get_headers(), data=json.dumps(data), **kwargs
        )
        return call_response

    # MESSAGE
    def create_message(self, list_id, data_dict, **kwargs):
        url = self.console_endpoint + "/Console/List/{list_id}/Email".format(
            list_id=list_id,
        )
        call_response = self.call_handler(
            "POST", url, data=json.dumps(data_dict), headers=self.get_headers(), **kwargs
        )
        return call_response

    def list_messages(self, list_id, status=None, filters=None, **kwargs):
        params = utils.filters_to_querystring(filters)
        if not status:
            url = self.console_endpoint + "/Console/List/{list_id}/Emails".format(
                list_id=list_id,
            )
        else:
            status = status.title()
            url = self.console_endpoint + "/Console/List/{list_id}/{status}/Emails".format(
                list_id=list_id,
                status=status,
            )
        call_response = self.call_handler("GET", url, params=params, headers=self.get_headers(), **kwargs)
        return call_response

    def read_message_detail(self, list_id, message_id, **kwargs):
        url = self.console_endpoint + "/Console/List/{list_id}/Email/{message_id}".format(
            list_id=list_id,
            message_id=message_id,
        )
        call_response = self.call_handler("GET", url, headers=self.get_headers(), **kwargs)
        return call_response

    def read_message_attachments(self, list_id, message_id, **kwargs):
        url = self.console_endpoint + "/Console/List/{list_id}/Email/{message_id}/Attachment".format(
            list_id=list_id,
            message_id=message_id,
        )
        call_response = self.call_handler("GET", url, headers=self.get_headers(), **kwargs)
        return call_response

    def add_attachment_to_message(self, list_id, message_id, slot, data_dict, **kwargs):
        url = self.console_endpoint + "/Console/List/{list_id}/Email/{message_id}/Attachment/{slot}".format(
            list_id=list_id,
            message_id=message_id,
            slot=slot,
        )
        call_response = self.call_handler(
            "POST", url, data=json.dumps(data_dict), headers=self.get_headers(), **kwargs
        )
        return call_response

    def delete_attachment_from_message(self, list_id, message_id, slot, **kwargs):
        url = self.console_endpoint + "/Console/List/{list_id}/Email/{message_id}/Attachment/{slot}".format(
            list_id=list_id,
            message_id=message_id,
            slot=slot,
        )
        call_response = self.call_handler("DELETE", url, headers=self.get_headers(), **kwargs)
        return call_response

    def update_message(self, list_id, message_id, data_dict, **kwargs):
        url = self.console_endpoint + "/Console/List/{list_id}/Email/{message_id}".format(
            list_id=list_id,
            message_id=message_id,
        )
        call_response = self.call_handler(
            "PUT", url, data=json.dumps(data_dict), headers=self.get_headers(), **kwargs
        )
        return call_response

    def send_message_to_list(self, list_id, message_id, **kwargs):
        url = self.console_endpoint + "/Console/List/{list_id}/Email/{message_id}/Send".format(
            list_id=list_id,
            message_id=message_id,
        )
        call_response = self.call_handler("POST", url, data=json.dumps(dict()), headers=self.get_headers(), **kwargs)
        return call_response.__repr__()

    def send_message_to_group(self, group_id, message_id, **kwargs):
        url = self.console_endpoint + "/Console/Group/{group_id}/Email/{message_id}/Send".format(
            group_id=group_id,
            message_id=message_id,
        )
        call_response = self.call_handler("POST", url, data=json.dumps(dict()), headers=self.get_headers(), **kwargs)
        return call_response.__repr__()

    def send_message_to_recipient(self, email, message_id, **kwargs):
        url = self.console_endpoint + "/Console/Email/Send"
        data = {
            "Email": email,
            "idMessage": message_id,
        }
        call_response = self.call_handler("POST", url, data=json.dumps(data), headers=self.get_headers(), **kwargs)
        return call_response

    def retrieve_sending_history(self, list_id, message_id, **kwargs):
        url = self.console_endpoint + "/Console/List/{list_id}/Email/{message_id}/SendHistory".format(
            list_id=list_id,
            message_id=message_id,
        )
        call_response = self.call_handler("GET", url, headers=self.get_headers(), **kwargs)
        return call_response

    # TAG
    def list_tags(self, list_id, tag_id=None, tag_name=None, **kwargs):
        url = self.console_endpoint + "/Console/List/{list_id}/Tags".format(
            list_id=list_id,
        )
        params = None
        filter_string = ''
        if tag_id:
            filter_string = "idTag=={tag_id}".format(tag_id=tag_id)
            if tag_name:
                filter_string += '&'
        if tag_name:
            filter_string += "Name=='{tag_name}'".format(
                tag_name=tag_name,
            )
        if filter_string:
            params = {
                "filterby": filter_string,
            }
        call_response = self.call_handler("GET", url, params=params, headers=self.get_headers(), **kwargs)
        return call_response

    def create_tag(self, list_id, tag_name, **kwargs):
        tag_name = '{quote}{tag_name}{quote}'.format(
            quote='"',
            tag_name=tag_name
        )
        url = self.console_endpoint + "/Console/List/{list_id}/Tag".format(
            list_id=list_id,
        )
        call_response = self.call_handler("POST", url, data=tag_name, headers=self.get_headers(), **kwargs)
        return call_response

    def modify_tag(self, list_id, data_dict, **kwargs):
        tag_id = data_dict['Id']
        url = self.console_endpoint + "/Console/List/{list_id}/Tag/{tag_id}".format(
            list_id=list_id,
            tag_id=tag_id,
        )
        call_response = self.call_handler(
            "PUT", url, data=json.dumps(data_dict), headers=self.get_headers(), **kwargs
        )
        return call_response

    def remove_tag(self, list_id, tag_id, **kwargs):
        url = self.console_endpoint + "/Console/List/{list_id}/Tag/{tag_id}".format(
            list_id=list_id,
            tag_id=tag_id,
        )
        call_response = self.call_handler("DELETE", url, headers=self.get_headers(), **kwargs)
        return call_response

    # STATISTIC BY MESSAGE
    def count_read_message_recipients(self, message_id, **kwargs):
        url = self.mail_statistics_endpoint + "/Message/{message_id}/Count/Recipients".format(
            message_id=message_id,
        )
        call_response = self.call_handler("GET", url, headers=self.get_headers(), **kwargs)
        return call_response

    def list_read_message_recipients(self, message_id, **kwargs):
        url = self.mail_statistics_endpoint + "/Message/{message_id}/List/Recipients".format(
            message_id=message_id,
        )
        call_response = self.call_handler("GET", url, headers=self.get_headers(), **kwargs)
        return call_response

    def count_opened_message_recipients(self, message_id, **kwargs):
        url = self.mail_statistics_endpoint + "/Message/{message_id}/Count/Views".format(
            message_id=message_id,
        )
        call_response = self.call_handler("GET", url, headers=self.get_headers(), **kwargs)
        return call_response

    def list_opened_message_recipients(self, message_id, **kwargs):
        url = self.mail_statistics_endpoint + "/Message/{message_id}/List/Views".format(
            message_id=message_id,
        )
        call_response = self.call_handler("GET", url, headers=self.get_headers(), **kwargs)
        return call_response

    def count_clicked_message_recipients(self, message_id, **kwargs):
        url = self.mail_statistics_endpoint + "/Message/{message_id}/Count/Clicks".format(
            message_id=message_id,
        )
        call_response = self.call_handler("GET", url, headers=self.get_headers(), **kwargs)
        return call_response

    def list_clicked_message_recipients(self, message_id, **kwargs):
        url = self.mail_statistics_endpoint + "/Message/{message_id}/List/Clicks".format(
            message_id=message_id,
        )
        call_response = self.call_handler("GET", url, headers=self.get_headers(), **kwargs)
        return call_response

    def count_clicked_link_recipients(self, message_id, **kwargs):
        url = self.mail_statistics_endpoint + "/Message/{message_id}/List/UrlClicks".format(
            message_id=message_id,
        )
        call_response = self.call_handler("GET", url, headers=self.get_headers(), **kwargs)
        return call_response

    def list_clicked_link_recipients(self, message_id, **kwargs):
        url = self.mail_statistics_endpoint + "/Message/{message_id}/List/UrlClickDetails".format(
            message_id=message_id,
        )
        call_response = self.call_handler("GET", url, headers=self.get_headers(), **kwargs)
        return call_response

    def count_bounced_message_recipients(self, message_id, **kwargs):
        url = self.mail_statistics_endpoint + "/Message/{message_id}/Count/Bounces".format(
            message_id=message_id,
        )
        call_response = self.call_handler("GET", url, headers=self.get_headers(), **kwargs)
        return call_response

    def list_bounced_message_recipients(self, message_id, **kwargs):
        url = self.mail_statistics_endpoint + "/Message/{message_id}/List/Bounces".format(
            message_id=message_id,
        )
        call_response = self.call_handler("GET", url, headers=self.get_headers(), **kwargs)
        return call_response

    # STATISTIC BY RECIPIENT
    def count_delivered_messages(self, recipient_id, **kwargs):
        url = self.mail_statistics_endpoint + "/Recipient/{recipient_id}/Count/Deliveries".format(
            recipient_id=recipient_id,
        )
        call_response = self.call_handler(
            "GET", url, headers=self.get_headers(), **kwargs
        )
        return call_response

    def list_delivered_messages(self, recipient_id, **kwargs):
        url = self.mail_statistics_endpoint + "/Recipient/{recipient_id}/List/Deliveries".format(
            recipient_id=recipient_id,
        )
        call_response = self.call_handler(
            "GET", url, headers=self.get_headers(), **kwargs
        )
        return call_response

    def count_opened_messages(self, recipient_id, **kwargs):
        url = self.mail_statistics_endpoint + "/Recipient/{recipient_id}/Count/Views".format(
            recipient_id=recipient_id,
        )
        call_response = self.call_handler(
            "GET", url, headers=self.get_headers(), **kwargs
        )
        return call_response

    def list_opened_messages(self, recipient_id, **kwargs):
        url = self.mail_statistics_endpoint + "/Recipient/{recipient_id}/List/Views".format(
            recipient_id=recipient_id,
        )
        call_response = self.call_handler(
            "GET", url, headers=self.get_headers(), **kwargs
        )
        return call_response

    def count_clicked_messages(self, recipient_id, **kwargs):
        url = self.mail_statistics_endpoint + "/Recipient/{recipient_id}/Count/Clicks".format(
            recipient_id=recipient_id,
        )
        call_response = self.call_handler(
            "GET", url, headers=self.get_headers(), **kwargs
        )
        return call_response

    def list_clicked_messages(self, recipient_id, **kwargs):
        url = self.mail_statistics_endpoint + "/Recipient/{recipient_id}/List/Clicks".format(
            recipient_id=recipient_id,
        )
        call_response = self.call_handler(
            "GET", url, headers=self.get_headers(), **kwargs
        )
        return call_response

    def count_clicked_link_messages(self, recipient_id, **kwargs):
        # TODO: verificare
        url = self.mail_statistics_endpoint + "/Recipient/{recipient_id}/Count/UrlClickDetails".format(
            recipient_id=recipient_id,
        )
        call_response = self.call_handler(
            "GET", url, headers=self.get_headers(), **kwargs
        )
        return call_response

    def list_clicked_link_messages(self, recipient_id, **kwargs):
        # TODO: verificare
        url = self.mail_statistics_endpoint + "/Recipient/{recipient_id}/List/UrlClickDetails".format(
            recipient_id=recipient_id,
        )
        call_response = self.call_handler(
            "GET", url, headers=self.get_headers(), **kwargs
        )
        return call_response

    def count_bounced_messages(self, recipient_id, **kwargs):
        url = self.mail_statistics_endpoint + "/Recipient/{recipient_id}/Count/Bounces".format(
            recipient_id=recipient_id,
        )
        call_response = self.call_handler(
            "GET", url, headers=self.get_headers(), **kwargs
        )
        return call_response

    def list_bounced_messages(self, recipient_id, **kwargs):
        url = self.mail_statistics_endpoint + "/Recipient/{recipient_id}/List/Bounces".format(
            recipient_id=recipient_id,
        )
        call_response = self.call_handler(
            "GET", url, headers=self.get_headers(), **kwargs
        )
        return call_response

    def count_unsubscribed_messages(self, recipient_id, **kwargs):
        url = self.mail_statistics_endpoint + "/Recipient/{recipient_id}/Count/Unsubscriptions".format(
            recipient_id=recipient_id,
        )
        call_response = self.call_handler(
            "GET", url, headers=self.get_headers(), **kwargs
        )
        return call_response

    def list_unsubscribed_messages(self, recipient_id, **kwargs):
        url = self.mail_statistics_endpoint + "/Recipient/{recipient_id}/List/Unsubscriptions".format(
            recipient_id=recipient_id,
        )
        call_response = self.call_handler(
            "GET", url, headers=self.get_headers(), **kwargs
        )
        return call_response


class MailUpClientSingleton(object):

    _client = None

    def __new__(cls, client_id, client_secret, username, password, *args, **kwargs):
        if not cls._client:
            cls._client = MailUpClient(client_id, client_secret, username, password)
            return cls._client
        else:
            return cls._client
