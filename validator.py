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

class MDSProviderApi(): 
    """
    Class representing an MDS provider API
    """
    
    def _get_mds_url(self):
        df = pd.read_csv(PROVIDERS_INFO_PATH)
        providers = df.to_dict(orient='records')
        for provider in providers:
            if provider['provider_name'].lower() == self.name.lower():
                return provider['mds_api_url']
        names = str([x['provider_name'] for x in providers])
        msg = "Provider {} not in list of providers {}".format(self.name, names)
        raise ProviderNotFoundError("ProviderNotFoundError", msg)

    def _compose_header(self):
        if self.name.lower() == 'bird':
            auth = 'Bird ' + self.token
            header = {'Authorization': auth, 'APP-Version': '3.0.0'}
        else:
            auth = 'Bearer ' + self.token
            header = {'Authorization': auth}
        return header
    
    def validate_trips(self): 
        """
        Validates the trips endpoint. Returns True if valid. 
        """
        r = requests.get(MDS_SCHEMA_PATH + "trips.json")
        schema = r.json()
        v = Draft4Validator(schema)
        r  = requests.get(self._get_mds_url() + self.post_fix + '/trips', headers = self._compose_header())  
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
        print("Validated Trips for {}".format(self.name))
        return True

    def validate_status_changes(self):
        """
        Validates the status_change endpoint
        """
        r = requests.get(MDS_SCHEMA_PATH + "status_changes.json")
        schema = r.json()
        v = Draft4Validator(schema)

        r  = requests.get(self._get_mds_url() + self.post_fix + '/status_changes', headers = self._compose_header())

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
        print("Validated Status Changes for {}".format(self.name))
        return True 

    def test_query_params(self):
        """
        Tests if you can pass query params to the APIs and get back data
        """
        pass
    def __init__(self, name, token, post_fix):
        self.name = name
        self.token = token
        self.post_fix = post_fix
        self.header = {'Authorization': "Bearer " + self.token}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Provide an MDS API to validate')
    parser.add_argument("--provider-name",type=str,
                        help="Name of the Provider that you are attempt to validate")

    parser.add_argument("--token",type=str,
                        help="Bearer Token for the provider that you are attempting to validate")
    parser.add_argument("--postfix", type=str,
                        help="if it exists, the post_fix (ie, city or version or both) from the MDS base url in providers.csv")
    

    parser.add_argument('--status-changes', dest='status_change', action='store_true')
    parser.add_argument('--trips', dest='trips', action='store_true')
    parser.set_defaults(status_change=False)
    parser.set_defaults(trips=False)
    args = parser.parse_args()
    if args.postfix: 
        api = MDSProviderApi(args.provider_name,args.token, args.postfix)
    else: 
        api = MDSProviderApi(args.provider_name, args.token, '')
    print("Attempting to validate {}".format(api.name))
    if args.trips:
        api.validate_trips()
    elif args.status_change:
        api.validate_status_changes()
    else: 
        api.validate_trips()
        api.validate_status_changes()
