import argparse
import jsonschema
from jsonschema import Draft4Validator
import requests
import pandas as pd

MDS_SCHEMA_PATH = "https://raw.githubusercontent.com/CityOfLosAngeles/mobility-data-specification/master/provider/"
PROVIDERS_INFO_PATH = "https://raw.githubusercontent.com/CityOfLosAngeles/mobility-data-specification/master/providers.csv"


class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class ProviderNotFoundError(Error):
    """
    Provider not found
    """

    def __init__(self, expression, message):
        self.expression = expression 
        self.message = message

def GetMdsUrl(provider_name):
    df = pd.read_csv(PROVIDERS_INFO_PATH)
    providers = df.to_dict(orient='records')
    for provider in providers:
        if provider['provider_name'].lower() == provider_name.lower():
            return provider['mds_api_url']
    names = str([x['provider_name'] for x in providers])
    msg = "Provider {} not in list of providers {}".format(provider_name, names)
    raise ProviderNotFoundError("ProviderNotFoundError", msg)

def ComposeHeader(provider_name, token):
    if provider_name.lower() == 'bird':
        auth = 'Bird ' + token
        header = {'Authorization': auth, 'APP-Version': '3.0.0'}
    else:
        auth = 'Bearer ' + token
        header = {'Authorization': auth}
    return header

class MDSProviderApi(): 
    """
    Class representing an MDS provider API
    """
    
    def validate_trips(self): 
        """
        Validates the trips endpoint. Returns True if valid. 
        """
        r = requests.get(MDS_SCHEMA_PATH + "trips.json")
        schema = r.json()
        v = Draft4Validator(schema)
        r  = requests.get(self.mds_url + '/trips', headers = self.headers)
        json = r.json()
        try: 
            jsonschema.validate(json,schema)
        except jsonschema.exceptions.ValidationError:
            print("Validation error encounted for {}".format(r.url))
            for error in sorted(v.iter_errors(json), key=str):
                print(error)
                for suberror in sorted(error.context, key=lambda e: e.schema_path):
                    print(list(suberror.schema_path), suberror.message, sep=", ")
            return False
        print("Validated Trips for {}".format(self.mds_url))
        return True

    def validate_status_changes(self):
        """
        Validates the status_change endpoint
        """
        r = requests.get(MDS_SCHEMA_PATH + "status_changes.json")
        schema = r.json()
        v = Draft4Validator(schema)

        r  = requests.get(self.mds_url + '/status_changes', headers = self.headers)

        json = r.json()
        try: 
            jsonschema.validate(json,schema)
        except jsonschema.exceptions.ValidationError:
            print("Validation error encounted for {}".format(r.url))
            for error in sorted(v.iter_errors(json), key=str):
                print(error)
                for suberror in sorted(error.context, key=lambda e: e.schema_path):
                    print(list(suberror.schema_path), suberror.message, sep=", ")
            return False
        print("Validated Status Changes for {}".format(self.mds_url))
        return True 

    def test_query_params(self):
        """
        Tests if you can pass query params to the APIs and get back data
        """
        pass
    def __init__(self, mds_url, headers):
        self.mds_url = mds_url
        self.headers = headers

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Provide an MDS API to validate')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--provider-name",type=str,
                       help="Name of the Provider that you are attempt to validate")
    group.add_argument("--mds-url",type=str,
                       help="Manual specification of MDS API to validate")

    parser.add_argument("--token",type=str,
                        help="Bearer Token for the provider that you are attempting to validate",
                        required=True)
    parser.add_argument("--postfix", type=str,
                        help="if it exists, the post_fix (ie, city or version or both) from the MDS base url in providers.csv")
    
    parser.add_argument('--status-changes', dest='status_change', action='store_true')
    parser.add_argument('--trips', dest='trips', action='store_true')
    parser.set_defaults(status_change=False)
    parser.set_defaults(trips=False)
    args = parser.parse_args()

    mds_url = args.mds_url
    if args.provider_name:
        mds_url = GetMdsUrl(args.provider_name)
        headers = ComposeHeader(args.provider_name, args.token)
    if args.postfix:
        mds_url += args.postfix
        headers = ComposeHeader("", args.token)

    api = MDSProviderApi(mds_url, headers)
    print("Attempting to validate {}".format(mds_url))
    if args.trips:
        api.validate_trips()
    elif args.status_change:
        api.validate_status_changes()
    else: 
        api.validate_trips()
        api.validate_status_changes()
