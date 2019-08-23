# AutoChannel UI
This is the UI front end in development for the autochannel-bot that runs for discord. The API backend is written in flask (python) and the frontend is in the vuejs framework. 

## How to develop?

The makefile is your friend, but have a few perquisites you will need to cover first.
You will need pipenv, make, gcc (linux) for compiling fun. This readme will not go
over all this, but should be straight forward. Some info about [pipenv](https://realpython.com/pipenv-guide/#pipenv-introduction)



### Running commands

#### make init
does the base install of the source package through pipenv that should already be installed,
if a local pipenv isn't yet setup this is when it will happen (python 3.6.8)

#### make check
Designed to do linting and pipenv checking for dependencies and such

#### make test
This is designed to install fakahbot package and testing packages if I ever decided to write tests for it :shrug:

#### make dist
Makes is dist package for system built on.

#### make live
This run only on image builds in my CI/CD pipeline just install the package in the image and pushes into image repo.


### After installing fakah-bot what do?

You will need to copy example.env to .env and update the value inside

| ENV Variable | Description | Required | Default |
| :----------- | :---------: | -------: | :-----: |
| `OAUTH2_CLIENT_ID`     | APP ID of your discordapp | NO | N/A |
| `OAUTH2_CLIENT_SECRET`      | discoard app secret | YES | N/A |
| `REDIS_URL`      | redis url (not yet implemented)| NO | N/A |

### Now Running the ui locally


```bash
pipenv run autochannel_backend --debug

second terminal
yarn run dev

```