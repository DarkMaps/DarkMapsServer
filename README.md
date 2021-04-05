# Dark Maps Server



>> A server for the Dark Maps project



This repository contains a simple server providing REST API calls to manage a messaging service using signal protocol encryption. It allows for storage and retrieval of all required keys, as well as the encrypted messages.



**DISCLAIMER - This project has no relation to Whisper Systems, the Signal Foundation or Signal app. It is intended for testing purposes only, and has not been tested at any point for security**



---

## Index

- [Installation](#installation)

- [Local Development](#local-development)

- [Testing](#testing)

- [Using In Production](#using-in-production)

- [API Documentation](#api-documentation)

  - [Authentication](#authentication)
  - [Two-Factor Authentication (2FA)](#two-factor-authentication-(2fa))
  - [Devices](#devices)
  - [Messages](#messages)
  - [Keys](#keys)

- [Testing Environment Variables](#testing-environment-variables)



---



## Installation

**Note:** This requires the python environment to have been correctly set up previously, typically using a virtual environment. Postgresql and psycopg2 must be available to the virtualenv. For example:
```
<!-- Install Postgresql -->
brew install postgresql
brew install openssl
brew install pkg-config libffi
pip install cffi
export LIBRARY_PATH=$LIBRARY_PATH:/usr/local/opt/openssl/lib/
pip3 install psycopg2
<!-- Set up VirtualEnv -->
virtualenv -p python3 .env
source .env/bin/activate
pip install -r requirements.txt
```

Below, for clarity, are the packages installed by requirements.txt.
```
pip install django==2.2.18
pip install pip install djangorestframework==3.11.2
pip install django-trench==0.2.2
pip install boto3==1.14.41
pip install djoser==2.1.0
pip install django-cors-headers==2.4.0
pip install django-username-email==2.2.4
```

---

## Local Development
Local development using an example sqlite database can easily be initiated using:
```
./development.sh
```
To access the settings used when executing /.development.sh use the following flag.
```
--settings=dark_maps.development_settings
```


## Testing
Automated tests can be initiated using:
```
./test.sh
```


---



## Using in production

Using this container safely in production may require the following environment variables to be set:



### 		Site Name
​		Used to properly label emails

```
- SITE_NAME
```

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

The following are optional if you wish to use CA Certificates

```
- DATABASE_SSLMODE
- DATABASE_CERT_NAME
```



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

  NB: To properly format the reset password emails you must also create a super user, log in to the admin site and edit the 'Sites' configuration.



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



### Logging

​	The server can be set up to pass logs to Cloudwatch using the following environment variables

```
- CLOUDWATCH_AWS_ID
- CLOUDWATCH_AWS_KEY
- CLOUDWATCH_AWS_DEFAULT_REGION
```



## Setting the site name and domain for emails

The Sites framework is used to correctly set urls and verbose names in emails. To set these variables create a super user, log into the admin site at "<URL>/admin/" then set the site details.

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
	identity_key: <String - The identity key, length 44 characters, base64 encoded>,
	registration_id: <Integer - The device registration ID>
	pre_keys: [
		{
			key_id: <Integer>,
			public_key: <String - Length 44 characters, base64 encoded>
		}
	],
	signed_pre_key: {
		key_id: <Integer>,
		public_key: <String - Length 44 characters, base64 encoded>,
		signature: <String - Length 88 characters, base64 encoded>
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

Requires token authentication.

```
/v1/<Sending user's registration ID>/messages/ POST

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
      code: 'no_recipient_user',
      message: 'Recipient does not exist'
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

Gets all outstanding messages for the signed in user. Requires token authentication.

```
/v1/<Receiving user's registration ID>/messages/ GET

Success <HTTP 200>:
	[
		{
			id: <Integer>,
			content: <String in JSON format as shown below>,
      recipient_address: <String>,
			sender_registration_id: <Integer>,
			sender_address: <String>
		},
		...
	]

JSON Content String:
  {
  	registration_id: <Integer - The recipient's registration ID>,
  	content: <Sring - The actual message content>
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
```



**Delete a message**

Deletes a message owned by the signed in user. Requires token authentication.

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

Allows a user to retrieve a prekey bundle for another user prior to starting communications. Requires token authentication.

```
/v1/prekeybundle/<recipient email>/<sender's device registration ID>/ GET

NB: <recipient email> must be Hex encoded.

Success <HTTP 200>:
	{
		address: <String>,
		identity_key: <String - The identity key, length 44 characters, base64 encoded>,
		registration_id: <Integer>,
		pre_key: {
      key_id: <Integer>,
      public_key: <String - Length 44 characters, base64 encoded>
    },
		signed_pre_key: {
      key_id: <Integer>,
      public_key: <String - Length 44 characters, base64 encoded>,
      signature: <String - Length 88 characters, base64 encoded>
    }
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

Send a list of new prekeys to the server. Requires token authentication.
```
/v1/<sender's device registration ID>/prekeys/ POST

Body:
  [
    {
      key_id: <Integer>,
      public_key: <String - Length 44 characters, base64 encoded>
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

Send a new signed prekey to the server. Requires token authentication.
```
/v1/<sender's device registration ID>/signedprekeys/ POST

Body:
  {
    key_id: <Integer>,
    public_key: <String - Length 44 characters, base64 encoded>,
    signature: <String - Length 88 characters, base64 encoded>
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

## Testing Environment Variables

Test environment variables locally using the following command. Create a file named `.environment` to set the environment variables.
```
./development-using-dot-env.sh
```
