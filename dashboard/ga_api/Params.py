from apiclient.discovery import build
import httplib2

from oauth2client.service_account import ServiceAccountCredentials
SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
DISCOVERY_URI = ('https://analyticsreporting.googleapis.com/$discovery/rest')
KEY_FILE_LOCATION = '/Users/duxiaoyang/Desktop/dashboard/ga_api/HelloAnalytics-server.p12'
SERVICE_ACCOUNT_EMAIL = 'new-dashboard@woven-environs-147905.iam.gserviceaccount.com'

def initialize_analyticsreporting():
    """Initializes an analyticsreporting service object.

    Returns:
    analytics an authorized analyticsreporting service object.
    """

    credentials = ServiceAccountCredentials.from_p12_keyfile(
        SERVICE_ACCOUNT_EMAIL, KEY_FILE_LOCATION, scopes=SCOPES)

    http = credentials.authorize(httplib2.Http())

    # Build the service object.
    analytics = build('analytics', 'v4', http=http, discoveryServiceUrl=DISCOVERY_URI)

    analytics=None
    return analytics



g_analytics=initialize_analyticsreporting()
g_h5_ID = '130800691'#h5
g_pc_ID='131320833'#p
class Params:
    #global g_analytics
    global g_pc_ID
    global g_h5_ID

    h5_ID = g_h5_ID
    pc_ID = g_pc_ID
    analytics=g_analytics
    #analytics=initialize_analyticsreporting()



    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            orig = super(Params, cls)
            cls._instance = orig.__new__(cls, *args, **kwargs)
        return cls._instance

