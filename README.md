# signal_server
>> A server for the signal protocol

This repository contains a simple server providing REST API calls to manage a messaging service using signal protocol encryption. It allows for storage and retrieval of all required keys, as well as the encrypted messages.

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

### User Management

**/auth/users POST**
Creates a new user.
```
{
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

### Devices

**/device POST**
Create a new device. Require JWT authentication.
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

**/device DELETE**
Deletes a device. Requires JWT authentication


### Messages

**/messages/localRegistrationId POST**

**/messages/localRegistrationId GET**

**/messages/localRegistrationId DELETE**

## Keys

**/prekeybundle/{recipientUsername}/{localRegistrationId} POST**

**prekeys/localRegistrationId**

**signedprekey/localRegistrationId**


