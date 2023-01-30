# ConvIn Google Calendar API Integration

## Prerequisites

- Python 3.x (I'd used Python 3.10)
- Django 4.x (I'd used Django 4.1.5)
- Google developer console account
- A google calendar

### Installing

1. Clone the repository
`git clone https://github.com/AvanishCodes/convin.git`

2. Create a virtual environment and activate it `python3 -m venv myenv source myenv/bin/activate`

3. Install the dependencies `pip install -r requirements.txt`

4. Create a project in the [Google developer console](https://console.developers.google.com/) and enable the Google Calendar API. Also, register the url `http://127.0.0.1:8000/rest/v1/calendar/redirect` as an authorized redirect URI.

5. In the developer console, navigate to the `Credentials` page, create a new OAuth client ID, and specify authorized redirect URIs.

6. Save the credentials from the same page in a file named `credentials.json` in the root directory of the project.

7. Start the development server `python3 manage.py runserver`

### Testing the integration

You can test the integration by sending GET requests to the URLs that trigger the views and checking the responses.

1. Open a web browser and navigate to the URL for the GoogleCalendarInitView. For example, if the URL for this view is `/rest/v1/calendar/init/`, you would navigate to `http://localhost:8000/rest/v1/calendar/init/`

2. The browser should redirect you to the Google authorization endpoint, where you will be prompted to enter your Google credentials and grant access to your calendar.

3. After granting access, the browser will redirect you to the URL for the GoogleCalendarRedirectView.

4. The view will handle the redirect request, get the access_token, and get the list of events in the user's calendar. The view will return the list of events in the response in json format.
