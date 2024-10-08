from datetime import datetime
from getpass import getpass
import json
import logging
import os
import requests
import sys
import termios
import time
import urllib

import onedrive_api.constants as c
from onedrive_api.utils import (
    get_long_user_response,
    handle_response_code,
)


class OneDriveAPIClient:
    def __init__(self):
        self.permissions = c.PERMISSIONS
        self.scope = ''
        for items in range(len(self.permissions)):
            self.scope = self.scope + self.permissions[items]
            if items < len(self.permissions)-1:
                self.scope = self.scope + '+'
        self.url = c.API_ROOT_URL
        self.auth_url = c.AUTH_URL
        self.auth_response_type = c.AUTH_RESPONSE_TYPE
        self.client_id = c.CLIENT_ID
        self.redirect_uri_quoted = urllib.parse.quote(c.REDIRECT_URI)


    def authenticate(self):
        logging.info('Click this link ' + self.auth_url + '?client_id=' + \
            self.client_id + '&scope=' + self.scope + '&response_type=' + \
            self.auth_response_type + '&redirect_uri=' + \
            self.redirect_uri_quoted)
        logging.info('Sign in to your account, copy the whole redirected URL.')
        logging.info('Note: "This site can\'t be reached." is not a problem.')
        
        code = get_long_user_response('Paste the URL here: ')
        
        self.token = code[
            (code.find('access_token') + len('access_token') + 1) : \
            (code.find('&token_type'))
        ]
        
        self.headers = {'Authorization': 'Bearer ' + self.token}
        
        response = self._response_get('me/drive/')

        return self.token
    

    def _response_get(self, endpoint: str) -> dict:
        response = json.loads(requests.get(f"{self.url}{endpoint}",
                                           headers = self.headers).text)
        handle_response_code(response)

        return response


    def list_root(self) -> None:
        items = self._response_get('me/drive/root/children')
        items = items['value']
        for entries in range(len(items)):
            print(items[entries]['name'], '| item-id >', items[entries]['id'])
        

    def list_dir(self, item_id: str) -> None:
        items = self._response_get(f"me/drive/items/{item_id}/children")['value']
        print(items)
        for entries in range(len(items)):
            print(entries)
            print(items[entries]['name'], '| item-id >', items[entries]['id'])


    def lookup_file(self, filename: str) -> str:
        items = self._response_get('me/drive/items/root/children')
        item_id = ''
        items = items['value']

        for entries in range(len(items)):
            if(items[entries]['name'] == filename):
                item_id = items[entries]['id']
                logging.info(f"Item-id of {filename}: {item_id}")
                break
        
        if(item_id==''):
            logging.error(filename, 'not found in the directory.')
        
        return item_id


    def delete_file(self, item_id: str) -> None:
        confirmation = input('Are you sure to delete the item? (Y/n):')
        if (confirmation.lower()=='y'):
            response = requests.delete(f"{self.url}/me/drive/items/{item_id}",
                                          headers=self.headers)
            if (response.status_code == 204):
                logging.info('Item gone! If need to recover, please check OneDrive Recycle Bin.')
        else:
            logging.warning("Item not deleted.")


    def download_file(self,
                      item_id: str,
                      output_path: str) -> None:
        response = requests.get(
            f"{self.url}/me/drive/items/{item_id}/content",
            headers=self.headers
        )
        try:
            with open (output_path, "wb") as f:
                f.write(response.content)
            logging.info("File succesfully downloaded")
        except Exception as e:
            logging.error(f"File download failed, {e}")