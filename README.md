# mds-validator
A package to automatically validate MDS APIs for compliance and testing purposes. 

To validate an API, you'll need an active Bearer token. 

For example, to validate the lime API, you can run `python validator.py --provider-name lime --token [YOUR TOKEN HERE] --postfix /los_angeles`. 

## Developing / installing

mds-validator uses pipenv. To install packages and run the script: 

1. `pipenv install`

2. `pipenv shell`

3. `python validator.py --your-commands-here`
