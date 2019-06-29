# signal_server



>> A server for the signal protocol



This repository contains a simple server providing REST API calls to manage a messaging service using signal protocol encryption. It allows for storage and retrieval of all required keys, as well as the encrypted messages.



**DISCLAIMER - This project has no relation to the Signal Foundation or Signal app, although it makes use of the underlying code provided in the [libsignal_protocol_javascript](https://github.com/signalapp/libsignal-protocol-javascript) package. It is intended for testing purposes only, and has not been tested at any point for security**



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



## TODO
- Check error codes
- DOCUMENTATION
- Remove admin interface



---



## Local Development
Local development using sqlite can easily be initiated using:
```
./development.sh
```

**Note:** This requires the python environment to have been correctly set up previously, typically using a virtual environment. For example:
```
virtualenv -p python3 .env
source .env/bin/activate
pip install -r requirements.txt
```



---



## Starting the server using docker swarm

A simple docker compose file is provided for example usage. This creates a simple entwork with a single instance of the container and a mysql database. The API is available on port 8000.
```
docker-compose up
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

	- EMAIL_BACKEND
	- EMAIL_HOST
	- EMAIL_PORT
	- EMAIL_USE_TLS
	- EMAIL_USE_SSL
	- EMAIL_TIMEOUT
	- EMAIL_SSL_KEYFILE
	- EMAIL_SSL_CERTFILE

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

**Note: Where the device registrationId is sent to the server it is the sending user's registration ID that is included, not the recipient.**

### Authentication

Authentication is provided using the Django [Djoser](https://djoser.readthedocs.io/en/latest/base_endpoints.html) and [Django Trench](https://django-trench.readthedocs.io/en/latest/endpoints.html) frameworks. All the documented Djoser **base** endpoints and **all** Django Trench endpoints are available. The most important of these are documented below.

**User Sign Up**

```
/auth/users/ POST

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

Note: With 2FA active the `auth/login/code` method must subsequently be called using the ephemeral token, as defined in the 2FA section.

```
/auth/login/ POST

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
/auth/logout/ POST

Body: <None>

Success <HTTP 204>
```



**User Delete**

Deletes a user and all their associated data. Requires token authentication.
```
/auth/users/me/ DELETE

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
/auth/password/reset/ POST

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
/auth/app/activate POST
```



**Activate 2FA Method**

Activates a 2FA method. Requires token authentication

```
/auth/<method>/activate/ POST

Body: <None>

Success <HTTP 200>
```



**Confirm 2FA Method**

Once activated, a 2FA method must be confirmed before it can be used. Requires token authentication.

```
/auth/<method>/activate/confirm/ POST

Body:
	{
		code: <Integer - A valid 2FA code for the selected method>
	}
	
Success <HTTP 200>
```



**Deactivate 2FA Method**

Requires token authentication.

```
/auth/<method>/deactivate POST

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
/auth/login/code/ POST

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

**/device/ POST**

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

**/device DELETE**

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

```
[
	<messageId>
]
```





## Keys

**/prekeybundle/<recipientEmail>/<deviceRegistrationID> GET**

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


