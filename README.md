gce-manager
===============

Google Compute Engine Manager

## Requirement

* Python 2.7 or later (tested under 2.7.7 and 3.6.5)
    * Pip Packages
        * google-auth:1.5.0
        * google-auth-httplib2: 0.0.3
        * google-api-python-client: 1.7.1

### Install and setup pip packages with pipenv

   $ mkdir myproject
   $ cd myproject
   $ cp /path/to/Pipfile .
   $ pipenv install
   $ pipenv shell
   $ # do works...
   $ exit # leave virtual environment

### Install and setup pip packages virtualenv pipenv

   $ virtualenv myproject
   $ cd myproject
   $ source ./bin/activate
   $ cp /path/to/requirements.txt .
   $ pip install -r requirements.txt
   $ # do works...
   $ deactivate # leave virtual environment

## Service account preparation

* Go to your Project page of GCP.
* Select  **APIs & Services** -> **Credentials** from left menu.
* Create Credentials: **Create Credentials** -> **Service account key**
    * Service account: New service account
    * Service account name: <as you like>
    * Role: Compute Engine -> Compute Admin
    * Key type: JSON


