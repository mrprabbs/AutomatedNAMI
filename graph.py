import base64
import json
from configparser import SectionProxy
from azure.identity import DeviceCodeCredential, ClientSecretCredential
from msgraph.core import GraphClient

# Graph API setup
import config


class Graph:
    """
    A class used to represent Microsoft Graph API Object. Allows program to access Graph REST API and send outlook
    emails as well as other functions
    ...
    Attributes
    ----------
    config: SectionProxy : configParser
        A proxy for a single section from a parser.

    Methods
    -------
    get_user_token(self):
        gets user access token
    get_user(self):
        gets user email
    send_mail(self, subject: str, body: str, recipient: str):
        creates JSON Post Request to send mail with a message, subject, recipient, and attachment of recruitment flyer
    """
    settings: SectionProxy
    device_code_credential: DeviceCodeCredential
    user_client: GraphClient
    client_credential: ClientSecretCredential
    app_client: GraphClient

    def __init__(self, config: SectionProxy):
        self.settings = config
        client_id = self.settings['clientId']
        tenant_id = self.settings['authTenant']
        graph_scopes = self.settings['graphUserScopes'].split(' ')

        self.device_code_credential = DeviceCodeCredential(client_id, tenant_id=tenant_id)
        self.user_client = GraphClient(credential=self.device_code_credential, scopes=graph_scopes)

    def get_user_token(self):
        """
        retrieval of user token from Graph API
        """
        graph_scopes = self.settings['graphUserScopes']
        access_token = self.device_code_credential.get_token(graph_scopes)
        return access_token.token

    def get_user(self):
        """
        retrieval of user display name from graph api using json request
        """
        endpoint = '/me'
        # Only request specific properties
        select = 'displayName,mail,userPrincipalName'
        request_url = f'{endpoint}?$select={select}'

        user_response = self.user_client.get(request_url)
        return user_response.json()

    def send_mail(self, subject: str, body: str, recipient: str):
        """
        creates JSON Post Request to send mail with a message, subject, recipient, and attachment of recruitment flyer

        Parameters
        ----------
        :param subject: str
            subject of the email
        :param body: str
            body of the email
        :param recipient: str
            email of person to which the email is being sent to
        """
        with open("flyer.pdf", "rb") as binary_file:
            media_content = base64.b64encode(binary_file.read())
        request_body = {
            'message': {
                'subject': subject,
                'body': {
                    'contentType': 'text',
                    'content': body
                },
                'toRecipients': [
                    {
                        'emailAddress': {
                            'address': recipient
                        }
                    }
                ],
                "attachments": [
                    {
                        "@odata.type": "#microsoft.graph.fileAttachment",
                        "name": "BeWellFlyer.pdf",
                        "contentType": "text/plain",
                        "contentBytes": media_content.decode('utf-8')
                    }
                ]
            }
        }

        request_url = config.request_url

        self.user_client.post(request_url,
                              data=json.dumps(request_body),
                              headers={'Authorization': self.get_user_token(), 'Content-Type': 'application/json'})
