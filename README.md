# signal_server



>> A server for the signal protocol



This repository contains a simple server providing REST API calls to manage a messaging service using signal protocol encryption. It allows for storage and retrieval of all required keys, as well as the encrypted messages.



**DISCLAIMER - This project has no relation to the Signal Foundation or Signal app. It is intended for testing purposes only, and has not been tested at any point for security**



---

## Index

- [TODO](#todo)

- [Local Development](#local-development)

- [Starting the server using docker swarm](#starting-the-server-using-docker-swarm)

- [Using In Production](#using-in-production)

- [API Documentation](#api-documentation)

  - [Authentication](#authentication)
  - [Two-Factor Authentication (2FA)](#two-factor-authentication-(2fa))
  - [Devices](#devices)
  - [Messages](#messages)
  - [Keys](#keys)



---



## Local Development
Local development using sqlite can easily be initiated using:
```
./development.sh
```

**Note:** This requires the python environment to have been correctly set up previously, typically using a virtual environment. MySql and mysqlclient must be available for the virtualenv install to be successful. For example:
```
<!-- Install MySql -->
brew install mysql
pip3 install mysqlclient
<!-- Set up VirtualEnv -->
virtualenv -p python3 .env
source .env/bin/activate
pip install -r requirements.txt
```



---



## Testing
Automated tests can be initiated using:
```
./test.sh
```

---


## Making Migrations

Due to the default database settings when making migrations in development use the following command
```
./manage.py makemigrations api --settings=signal_server.development_settings
```


---



## Using in production

Using this container safely in production may require the following environment variables to be set:





### 		Django Secret
​		Set this by passing an environment variable to your container as

```
- DJANGO_SECRET_KEY
```

​		This is essential. Leaving the default key in place is a major security risk.



### 		Database
​		You will most likely want to connect to an external database such as Amazon RDS. To do this pass the following environment variables to the container:

```
- DATABASE_NAME
- DATABASE_USER
- DATABASE_PASSWORD
- DATABASE_HOST
- DATABASE_PORT
- DJANGO_ALLOWED_HOSTS (passed in as a string of allowed hosts separated by spaces eg. 'foo.com baa.com')
```

​		This is essential. Leaving the default user and password in place is a major security risk.



### 		Email

​		You will need to set up external email using SMTP in order to allow your users to rset their passwords. Do so by passing the following environment variables to your container. See the [Django Docs](https://docs.djangoproject.com/en/2.2/topics/email/#email-backends)


```
	- EMAIL_BACKEND
	- EMAIL_HOST
	- EMAIL_PORT
	- EMAIL_USE_TLS
	- EMAIL_USE_SSL
	- EMAIL_TIMEOUT
	- EMAIL_SSL_KEYFILE
	- EMAIL_SSL_CERTFILE
```

​		This is essential in production to allow password reset emails to be sent.



### 		Two Factor Authentication

​	The following environment variables alter the action of the 2FA manager. See [Django Trench Docs](https://django-trench.readthedocs.io/en/latest/settings.html)

```
- 2FA_FROM_EMAIL
- 2FA_APPLICATION_NAME
```

​		These settings are not essential, but will improve the appearance of the 2FA flow for your users.



### Memcache

​	The following environment variables control the cache settings for the server. By default a simple in memory local cache is used. Setting this variable will switch to a memcache server.

```
- MEMCACHE_LOCATION
```

​		By default only a local cache will be used. This means that in a  rate limiting will not perform correctly, as each



---



## API Documentation

**Note: Where the device registration_id is sent to the server it is the sending user's registration ID that is included, not the recipient.**

### Authentication

Authentication is provided using the [Django Djoser](https://djoser.readthedocs.io/en/latest/base_endpoints.html) and [Django Trench](https://django-trench.readthedocs.io/en/latest/endpoints.html) frameworks. All the documented Djoser **base** endpoints and **all** Django Trench endpoints are available. The most important of these are documented below.

**User Sign Up**

```
/v1/auth/users/ POST

Body:
  {
    email: <String - The user's email for login>,
    password: <String - The user's password>
  }

Success <HTTP 201>:
	{
		email: <String>,
		id: <Integer>
	}
```



**User Log In**

The provided auth token should be used in the Authorization HTTP header to authorise all further calls to the server.

Note: With 2FA active the `/v1/auth/login/code` method must subsequently be called using the ephemeral token, as defined in the 2FA section.

```
/v1/auth/login/ POST

Body:
  {
    email: <String>,
    password: <String>
  }

# Without 2FA Active
Success <HTTP 200>:
	{
		auth_token: <String>
	}

# With 2FA Active
Success <HTTP 200>:
	{
		ephemeral_token: <String>,
		method: <String>
	}
```



**User Log Out**

Logs the user out of the server by invalidating their authorization token. Requires token authentication.

```
/v1/auth/logout/ POST

Body: <None>

Success <HTTP 204>
```



**User Delete**

Deletes a user and all their associated data. Requires token authentication.
```
/v1/auth/users/me/ DELETE

Body:
  {
  	currentPassword: <String>
  }

 Success <HTTP 204>
```



**Reset Password**

Allows user to reset password by sending an email with a reset link. Does *<u>not</u>* require authentication.

Note: For security reasons this will always return a 204 code, regardless of whether the email provided is registered on the server.

```
/v1/auth/password/reset/ POST

Body:
  {
    email: <String>
  }

Success <HTTP 204>
```





### Two-Factor Authentication (2FA)

Two factor codes can be provided through either email or QR code apps. The method names ( `<method>` ) are defined below:

```
<method>

Email method: 'email'
QR code method: 'app'
```

For example, to activate the QR code method a call would be made to the following endpoint:

```
/v1/auth/app/activate POST
```



**Activate 2FA Method**

Activates a 2FA method. Requires token authentication

```
/v1/auth/<method>/activate/ POST

Body: <None>

Success <HTTP 200>
```



**Confirm 2FA Method**

Once activated, a 2FA method must be confirmed before it can be used. Requires token authentication.

```
/v1/auth/<method>/activate/confirm/ POST

Body:
	{
		code: <Integer - A valid 2FA code for the selected method>
	}

Success <HTTP 200>
```



**Deactivate 2FA Method**

Requires token authentication.

```
/v1/auth/<method>/deactivate POST

Body:
	{
		code: <Integer - A valid 2FA code for the selected method>
	}

Success <HTTP 204>
```



**2FA Login**

This is the second step of the 2FA login process, using the ephemeral token provided by the `/auth/login/` method (defined above) and a 2FA code.

If successful this method will return an auth_token to be used in the Authorization header.

```
/v1/auth/login/code/ POST

Body:
	{
		ephemeral_token: <String - ephemeral_token provided by first login step>
		code: <Integer - 2FA code provided by one active method>
	}

Success <HTTP 200>:
	{
		auth_token: <String>
	}
```


### Devices



**Create a device**

Requires token authentication


```
/v1/devices/ POST

Body:
{
	address: <String - The device address>,
	identity_key: <String - The identity key, length 32 characters>,
	registration_id: <Integer - The device registration ID>,
	signingKey: <String - The device signing key, length 32 characters>
	pre_keys: [
		{
			key_id: <Integer>,
			public_key: <String - Length 32 characters>
		}
	],
	signed_pre_key: {
		key_id: <Integer>,
		public_key: <String - Length 32 characters>,
		signature: <String - Length 64 characters>
	}
}

Success <HTTP 201>:
	{
		code: 'device_created',
		message: 'Device successfully created'
	}

Errors:

	Incorrect arguments provided:
		<HTTP 403>
		{
    	code: 'incorrect_arguments',
      message: 'Incorrect arguments were provided in the request',
      explanation: <An explanation of the errors - optional>
    }

  Device already exists:
  	<HTTP 403>
  	{
      code: 'device_exists',
      message: 'A device has already been created for this user'
  	}

```



**Delete a device**

Requires token authentication



```
/v1/devices/ DELETE

Body: <None>

Success <HTTP 204>

Errors:

	No device available to delete:
		<HTTP 404>
		{
      code: 'no_device',
      message: 'User has not yet registered a device'
  	}
```







### Messages



**Send a new message**

Requires token authentication and request signing.

```
/v1/<Sending user's device ID>/messages/ POST

Body:
{
	recipient: <String - The email address of the recipient in plain text>,
	message: <String - A JSON string in the format below>
}

JSON Message String:
{
	registration_id: <Integer - The recipient's registration ID>,
	content: <Sring - The actual message content>
}

Success <HTTP 201>:
	{
		id: <Integer>,
		content: <String>,
		sender_address: <String>
		sender_registration_id: <Integer>
		recipient_address: <String>
	}

Errors:
	Incorrect arguments provided:
		<HTTP 403>
		{
    	code: 'incorrect_arguments',
      message: 'Incorrect arguments were provided in the request',
      explanation: <An explanation of the errors - optional>
    }
  Invalid recipient email:
  	<HTTP 400>
  	{
      code: 'invalid_recipient_email',
      message: 'The email provided for the recipient is incorrectly formatted'
  	}
  Sending user has no registered device:
  	<HTTP 404>
  	{
      code: 'no_device',
      message: 'User has not yet registered a device'
  	}
  Sending user's device has changed:
  	<HTTP 403>
  	{
     	code: 'device_changed',
      message: 'Own device has changed'
  	}
  Recipient doesn't exist:
  	<HTTP 404>
  	{
      code: 'no_recipient',
      message: 'The recipient for your message does not exist'
  	}
  Recipient doesn't have a registered device
  	<HTTP 404>
  	{
      code: 'no_recipient_device',
      message: 'Recipient has not yet registered a device'
  	}
  The recipient's device has changed
  	<HTTP 403>
  	{
      code: 'recipient_identity_changed',
      message: 'Recipients device has changed'
  	}
```



**Get messages for user**

Gets all outstanding messages for the signed in user. Requires token authentication and request signing.

```
/v1/<Receiving user's registration ID>/messages/ GET

Success <HTTP 200>:
	[
		{
			id: <Integer>,
			created: <Date>,
			content: <String>,
			sender_registration_id: <Integer>,
			sender_address: <String>
		},
		...
	]

Errors:
	Incorrect arguments provided:
		<HTTP 403>
		{
    	code: 'incorrect_arguments',
      message: 'Incorrect arguments were provided in the request',
      explanation: <An explanation of the errors - optional>
    }
  Receiving user has no registered device:
  	<HTTP 404>
  	{
      code: 'no_device',
      message: 'User has not yet registered a device'
  	}
  Receiving user's device has changed:
  	<HTTP 403>
  	{
     	code: 'device_changed',
      message: 'Own device has changed'
  	}
```



**Delete a message**

Deletes a message owned by the signed in user. Requires token authentication and request signing.

```
/v1/<User's own registration ID>/messages/

Body:
[
	<message_id>,
	...
]

Success <HTTP 200>:
[
	<Response>
]

For each message id passed to the delete method one of the following responses can be provided:
	1) 'message_deleted'
	2) 'not_message_owner'
	3) 'non-existant_message'

Errors:
	Incorrect arguments provided:
		<HTTP 403>
		{
    	code: 'incorrect_arguments',
      message: 'Incorrect arguments were provided in the request',
      explanation: <An explanation of the errors - optional>
    }
  Receiving user has no registered device:
  	<HTTP 404>
  	{
      code: 'no_device',
      message: 'User has not yet registered a device'
  	}
  Receiving user's device has changed:
  	<HTTP 403>
  	{
     	code: 'device_changed',
      message: 'Own device has changed'
  	}
```





## Keys

**Get a prekey bundle**

Allows a user to retrieve a prekey bundle for another user prior to starting communications. Requires token authentication and request signing.

```
/v1/prekeybundle/<recipient email>/<sender's device registration ID>/ GET

NB: <recipient email> must be Hex encoded.

Success <HTTP 200>:
	{
		address: <String>,
		identity_key: <String>,
		registration_id: <Integer>,
		pre_key: <String>,
		signed_pre_key: <String>
	}

Errors:
	Incorrect arguments provided:
		<HTTP 403>
		{
    	code: 'incorrect_arguments',
      message: 'Incorrect arguments were provided in the request',
      explanation: <An explanation of the errors - optional>
    }
  Receiving user has no registered device:
  	<HTTP 404>
  	{
      code: 'no_device',
      message: 'User has not yet registered a device'
  	}
  Receiving user's device has changed:
  	<HTTP 403>
  	{
     	code: 'device_changed',
      message: 'Own device has changed'
  	}
  The recipient does not have a registered device:
  	<HTTP 404>
  	{
      code: 'no_recipient_device',
      message: 'Recipient has not yet registered a device'
		}
```



**Provide new prekeys **

Send a list of new prekeys to the server. Requires token authentication and request signing.
```
/v1/<sender's device registration ID>/prekeys/ POST

Body:
  [
    {
      key_id: <Integer>,
      public_key: <String>
    },
    ...
  ]

Success <HTTP 200>:
	{
		"code": "prekeys_stored",
		"message": "Prekeys successfully stored"
	}

Errors:
	Incorrect arguments provided:
		<HTTP 403>
		{
    	code: 'incorrect_arguments',
      message: 'Incorrect arguments were provided in the request',
      explanation: <An explanation of the errors - optional>
    }
    NOTE: This will be returned if any of the prekeys you provided was invalid.
  Sending user has no registered device:
  	<HTTP 404>
  	{
      code: 'no_device',
      message: 'User has not yet registered a device'
  	}
  Sending user's device has changed:
  	<HTTP 403>
  	{
     	code: 'device_changed',
      message: 'Own device has changed'
  	}
  The maximum number of allowed prekeys has already been stored:
  	<HTTP 400>
  	{
      code: 'reached_max_prekeys',
      message: 'User has reached the maximum number of prekeys allowed'
  	}
  One of the provided prekey's IDs already exists
  	<HTTP 400>
  	{
      code: 'prekey_id_exists',
      message: 'A prekey with that key_id already exists'
  	}
```



**Provide a new signed pre key**

Send a new signed prekey to the server. Requires token authentication and request signing.
```
/v1/<sender's device registration ID>/signedprekeys/ POST

Body:
  {
    key_id: <Integer>,
    public_key: <String>,
    signature: <String>
  }

Success <HTTP 200>:
	{
		code: 'signed_prekey_stored',
		message: 'Signed prekey successfully stored'
	}

Errors:
	Incorrect arguments provided:
		<HTTP 403>
		{
    	code: 'incorrect_arguments',
      message: 'Incorrect arguments were provided in the request',
      explanation: <An explanation of the errors - optional>
    }
  Sending user has no registered device:
  	<HTTP 404>
  	{
      code: 'no_device',
      message: 'User has not yet registered a device'
  	}
  Sending user's device has changed:
  	<HTTP 403>
  	{
     	code: 'device_changed',
      message: 'Own device has changed'
  	}
```
