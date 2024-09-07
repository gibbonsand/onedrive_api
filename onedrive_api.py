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


logger = logging.getLogger()


class OneDriveAPI:
    def __init__(self):
        self.PERMISSIONS = c.PERMISSIONS
        self.SCOPE = ''
        for items in range(len(self.PERMISSIONS)):
            self.SCOPE = self.SCOPE + self.PERMISSIONS[items]
            if items < len(self.PERMISSIONS)-1:
                self.SCOPE = self.SCOPE + '+'
        self.URL = c.API_ROOT_URL
        self.AUTH_URL = c.AUTH_URL
        self.AUTH_RESPONSE_TYPE = c.AUTH_RESPONSE_TYPE
        self.CLIENT_ID = c.CLIENT_ID
        self.REDIRECT_URI_QUOTED = urllib.parse.quote(c.REDIRECT_URI)


    def authenticate(self):
        print('Click over this link ' + self.AUTH_URL + '?client_id=' + \
            self.CLIENT_ID + '&scope=' + self.SCOPE + '&response_type=' + \
            self.AUTH_RESPONSE_TYPE + '&redirect_uri=' + \
            self.REDIRECT_URI_QUOTED)
        print('Sign in to your account, copy the whole redirected URL.')
        print('Note: "This site can\'t be reached." is not a problem.')
        
        code = get_long_user_response('Paste the URL here: ')
        
        self.token = code[
            (code.find('access_token') + len('access_token') + 1) : \
            (code.find('&token_type'))
        ]
        
        self.HEADERS = {'Authorization': 'Bearer ' + self.token}
        
        response = self._response_get('me/drive/')

        return self.token
    

    def _response_get(self, endpoint: str) -> dict:
        response = json.loads(requests.get(f"{self.URL}{endpoint}",
                                          headers = self.HEADERS).text)
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
                print('Item-id of', filename, ':', item_id)
                break
        
        if(item_id==''):
            print(filename, 'not found in the directory.')
        
        return item_id


    def delete_file(self, item_id: str) -> None:
        confirmation = input('Are you sure to delete the item? (Y/n):')
        if (confirmation.lower()=='y'):
            response = requests.delete(f"{self.URL}/me/drive/items/{item_id}",
                                          headers=self.HEADERS)
            if (response.status_code == 204):
                print('Item gone! If need to recover, please check OneDrive Recycle Bin.')
        else:
            print("Item not deleted.")


    def download_file(self,
                      item_id: str,
                      output_path: str) -> None:
        response = requests.get(
            f"{self.URL}/me/drive/items/{item_id}/content",
            headers=self.HEADERS
        )
        try:
            with open (output_path, "wb") as f:
                f.write(response.content)
            print("File succesfully downloaded")
        except Exception as e:
            print(f"File download failed, {e}")
    
