# signal_server
>> A server for the signal protocol

This repository contains a simple server providing REST API calls to manage a messaging service using signal protocol encryption. It allows for storage and retrieval of all required keys, as well as the encrypted messages.

## Local Development
Local development using sqlite can easily be initiated using:
```
./server/development.sh
```

**Note:** This requires the python environment to have been correctly set up previously, typically using a virtual environment. For example:
```
virtualenv -p python3 .env
source .env/bin/activate
pip install -r requirements.txt
```

## Starting the server using docker swarm
A simple docker compose file is provided for example usage. This creates a simple entwork with a single instance of the container and a mysql database. The API is available on port 8000.
```
docker-compose up
```

## Using in production
Using this container in production will require a few extra variables to be set

### Django Secret
Set this by passing an environment variable to your container as DJANGO_SECRET_KEY.

### Database
You will most likely want to connect to an external database such as Amazon RDS. To do this pass the following environment variables to the container:
    - 'DATABASE_NAME'
    - 'DATABASE_USER'
    - 'DATABASE_PASSWORD'
    - 'DATABASE_HOST'
    - 'DATABASE_PORT'
    - 'DJANGO_ALLOWED_HOSTS' (passed in as a string of allowed hosts separated by spaces eg. 'foo.com baa.com')

## API Documentation

Note: Where the device registrationId is sent to the server it is always the transmitting user's registration ID, no the recipient.

### User Management

**/auth/users POST**

Creates a new user.
```
{
	email: <String>,
    username: <String>,
    password: <String>
}
```

**/auth/jwt/create POST**

Returns a JWT allowing access to the service. This is the only way to access the other API points
```
{
    username: <String>,
    password: <String>
}
```

**/auth/users/me DELETE**

Deletes a user and all their associated data. Requires JWT authentication.

**/auth/password/reset POST**

Allows user to reset password.
```
{
	email: <String>
}
```

### Devices

**/device/<deviceRegistrationID> POST**

Create a new device. Requires JWT authentication.
Body:
```
{
	address: <String>,
	identityKey: <String>,
	registrationId: <Integer>,
	preKeys: [
		{
			keyId: <Integer>,
			publicKey: <String>
		}
	],
	signedPreKey: {
		keyId: <Integer>,
		publicKey: <String>,
		signature: <String>
	}
}
```

**/device/<deviceRegistrationID> DELETE**

Deletes a device. Requires JWT authentication


### Messages

**/messages/<deviceRegistrationID> POST**

Sends a new message. Requires JWT authentication.
Body:
```
{
	recipient: <String>,
	message: <String>
}
```

**/messages/<deviceRegistrationID> GET**

Gets all outstanding messages for a user. Requires JWT authentication.

**/messages/<deviceRegistrationID> DELETE**

Deletes a message owned by the user. Requires JWT authentication.

## Keys

**/prekeybundle/<recipientUsername>/<deviceRegistrationID> GET**

Gets a prekey bundle in anticipation of sending an initial message. Requires JWT authentication.

**prekeys/<deviceRegistrationID> POST**

Send a list of new prekeys to the server. Requires JWT authentication.
Body:
```
[
	{
		keyId: <Integer>,
		publicKey: <String>
	}
]
```

**signedprekey/<deviceRegistrationID> POST**

Send a new signed prekey to the server. Requires JWT authentication.
Body:
```
{
	keyId: <Integer>,
	publicKey: <String>,
	signature: <String>
}
```


