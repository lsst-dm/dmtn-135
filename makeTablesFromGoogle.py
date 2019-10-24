#!/usr/bin/env python3
# To access google you have to do some setup https://developers.google.com/sheets/api/quickstart/python
# roughly you must create a client secret for OAUTH using this wizard
# https://console.developers.google.com/start/api?id=sheets.googleapis.com
# Accept the blurb and go to the APIs
# click CANCEL on the next screen to get to the "create credentials"
# hit create credentials choose OATH client
# Configure a product - just put in a name like "LSST DOCS"
# Creat web application id
# Give it a name hit ok on the next screen
# now you can download the client id - call it client_secret.json as expected below.
# You have to do this once to allow the script to access yuour google stuff from this machine


import httplib2
import os

from googleapiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python DMTN-135'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ' + credential_path)
    return credentials


def outtail(tout):
    print("\\end{longtable} \\normalsize", file=tout)
    tout.close()
    return


def outhead(ncols, tout, name, cap):
    print("\\tiny \\begin{longtable} {", file=tout, end='')
    c = 1
    print(" |p{0.22\\textwidth} ", file=tout, end='')
    for c in range(1, ncols + 1):
        print(" |r ", file=tout, end='')
    print("|} ", file=tout, )
    print("\\caption{%s \\label{tab:%s}}\\\\ " % (cap, name), file=tout)
    print(r"\hline ", file=tout)
    return


def outputrow(tout, pre, row, cols, skip):
    skipped = 0
    for i in range(cols):
        if (i > 0 and skipped < skip):
            skipped = skipped + 1
        else:
            try:
                print("%s{%s}" % (pre, fixTex(row[i])), end='', file=tout)
            except IndexError:
                pass
            if i < cols-1:
                print("&", end='', file=tout)
    print(" \\\\ \\hline", file=tout)


def fixTex(text):
    ret = text.replace("_", "\\_")
    ret = ret.replace("/", "/ ")
    ret = ret.replace("$", "\\$")
    return ret


def main():
    """
    grab the sizing sheet and do whatever
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)


    spreadsheetId = '1DiFTjsC4dP8XyOV7-uF0zwkl0r0jMuW9U9uELejpmn8'
    rangeName = 'Model!A1:H'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])

    name = ''
    tout = ''

    if not values:
        print('No data found.')
    else:
        cols = 0
        skip = 0
        for row in values:
            if (row and 'Table' in row[0]):  # got a new table
                if name:
                    outtail(tout)
                vals = row[0].split(' ')
                name = vals[1]
                print("Create new table %s" % name)
                tout = open(name + '.tex', 'w')

                cap = row[1]
                cols = int(row[2])
                skip = int(row[3])

                outhead(cols-skip, tout, name, cap)
            else:
                if name and row:
                    if row[0].startswith('Year') or row[0].startswith('Total'):
                        # print headeri/total in bold
                        outputrow(tout, "\\textbf", row, cols, skip)
                    else:
                        outputrow(tout, "", row, cols, skip)
    outtail(tout)


if __name__ == '__main__':
    main()
