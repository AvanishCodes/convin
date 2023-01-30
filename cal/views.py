import os

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

CLIENT_SECRETS_FILE = "credentials.json"
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]
REDIRECT_URL = 'http://127.0.0.1:8000/rest/v1/calendar/redirect'
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'


def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }


class GoogleCalendarInitView(APIView):
    @swagger_auto_schema()
    def get(self, request, *args, **kwargs):
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=SCOPES)

        # The URI created here must exactly match one of the authorized redirect URIs
        # for the OAuth 2.0 client, which you configured in the API Console. If this
        # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
        # error.
        flow.redirect_uri = REDIRECT_URL

        authorization_url, state = flow.authorization_url(
            # Enable offline access so that you can refresh an access token without
            # re-prompting the user for permission. Recommended for web server apps.
            access_type='offline',
            # Enable incremental authorization. Recommended as a best practice.
            include_granted_scopes='true')

        # Store the state so the callback can verify the auth server response.
        request.session['state'] = state

        return Response({"authorization_url": authorization_url}, status=status.HTTP_200_OK)


class GoogleCalendarRedirectView(APIView):
    state_param = openapi.Parameter(
        'state', openapi.IN_QUERY, description="state", type=openapi.TYPE_STRING)
    code_param = openapi.Parameter(
        'code', openapi.IN_QUERY, description="code", type=openapi.TYPE_STRING)
    scope_param = openapi.Parameter(
        'scope', openapi.IN_QUERY, description="scope", type=openapi.TYPE_STRING)

    @swagger_auto_schema([state_param, code_param, scope_param])
    def get(self, request, *args, **kwargs):
        # Specify the state when creating the flow in the callback so that it can
        # verified in the authorization server response.
        # state = request.session['state']
        state = request.GET.get('state')

        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
        flow.redirect_uri = REDIRECT_URL

        # Use the authorization server's response to fetch the OAuth 2.0 tokens.
        authorization_response = request.get_full_path()
        flow.fetch_token(authorization_response=authorization_response)

        # Save credentials back to session in case access token was refreshed.
        # ACTION ITEM: In a production app, you likely want to save these
        # credentials in a persistent database instead.
        credentials = flow.credentials
        request.session['credentials'] = credentials_to_dict(credentials)

        # Check if credentials are in session
        if 'credentials' not in request.session:
            return redirect('v1/calendar/init')

        # Load credentials from the session.
        credentials = google.oauth2.credentials.Credentials(
            **request.session['credentials'])

        # Use the Google API Discovery Service to build client libraries, IDE plugins,
        # and other tools that interact with Google APIs.
        # The Discovery API provides a list of Google APIs and a machine-readable "Discovery Document" for each API
        service = googleapiclient.discovery.build(
            API_SERVICE_NAME, API_VERSION, credentials=credentials)

        # Returns the calendars on the user's calendar list
        calendar_list = service.calendarList().list().execute()

        # Getting user ID which is his/her email address
        # calendar_id = calendar_list['items'][0]['id']
        calendar_ids = []
        for calendar in calendar_list['items']:
            calendar_ids.append(calendar['id'])

        # Getting all events associated with an account
        events = []
        for calendar_id in calendar_ids:
            temp_events = events.append(service.events().list(calendarId=calendar_id).execute())
            if temp_events:
                for event in temp_events:
                    events.append(event)

        events_list_append = []
        # Save the events in a json file
        # json_file = open('events.json', 'w')
        # json_file.write(str(events))
        # json_file.close()
        if not events:
            return Response({"message": "No data found or user credentials invalid."})
        else:
            for events_list in events:
                events_list_append.append(events_list)
                return Response({"events": events_list_append})
        return Response({"error": "calendar event aren't here"})
