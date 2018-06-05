gce-manager
===============

Google Compute Engine Manager

## Requirement

* Python (tested under 3.6.5 only)
    * Pip Packages
        * google-auth:1.5.0
        * google-auth-httplib2: 0.0.3
        * google-api-python-client: 1.7.1
        * oauth2client: 4.1.2

### Install and setup pip packages by pipenv

   $ mkdir myproject
   $ cd myproject
   $ cp /path/to/Pipfile .
   $ pipenv install
   $ pipenv shell

## Service account preparation

* Go to your Project page of GCP.
* Select  **APIs & Services** -> **Credentials** from left menu.
* Create Credentials: **Create Credentials** -> **Service account key**
    * Service account: New service account
    * Service account name: <as you like>
    * Role: Compute Engine -> Compute Admin
    * Key type: JSON


