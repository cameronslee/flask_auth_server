# Flask OAuth2.0 Server

## Description
Full implementation of OAuth 2.0 Authorization Code Flow as described in [RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749#autoid-3)
```
     +----------+
     | Resource |
     |   Owner  |
     |          |
     +----------+
          ^
          |
         (B)
     +----|-----+          Client Identifier      +---------------+
     |         -+----(A)-- & Redirection URI ---->|               |
     |  User-   |                                 | Authorization |
     |  Agent  -+----(B)-- User authenticates --->|     Server    |
     |          |                                 |               |
     |         -+----(C)-- Authorization Code ---<|               |
     +-|----|---+                                 +---------------+
       |    |                                         ^      v
      (A)  (C)                                        |      |
       |    |                                         |      |
       ^    v                                         |      |
     +---------+                                      |      |
     |         |>---(D)-- Authorization Code ---------'      |
     |  Client |          & Redirection URI                  |
     |         |                                             |
     |         |<---(E)----- Access Token -------------------'
     +---------+       (w/ Optional Refresh Token)
```

# Instructions

## Install Required Packages
Can setup venv using requirements.txt

## Install OpenSSL
| OS                    | Instructions                                                                |
|-----------------------|-----------------------------------------------------------------------------|
| Linux (Debian/Ubuntu) | `sudo apt-get install openssl`                                              |
| macOS                 | (with [Homebrew](https://brew.sh/) package manager)  `brew install openssl` |
| Windows               | See [here](https://wiki.openssl.org/index.php/Binaries) for instructions.   |

## Generate Keys
### Generate Private Key (used to generate access tokens, stored in auth server)
```
openssl genrsa -out ./auth/private_key.pem 2048
```

### Generate Public Key (used to verify access tokens, stored in resource and client servers)
```
openssl rsa -in ./auth/private_key.pem -pubout -outform PEM -out ./client/public_key.pem

openssl rsa -in ./auth/private_key.pem -pubout -outform PEM -out ./api/public_key.pem
```
## Setup DB
```
cd auth 

export FLASK_APP=auth_server

flask db-init
```
### Sample Population Script via SQLITE3 CLI (emulates registering application)
```
INSERT INTO users (username, password) VALUES('foo', 'bar')

INSERT INTO clients (client_id, redirect_uri) VALUES('foo-client-id', 'http://localhost:8000/callback')

INSERT INTO applications(client_id, redirect_uri, client_secret) VALUES('foo-client-id', 'http://localhost:8000/callback', 'foo-client-secret')
```

## Run Servers
#### Client Server: port 8000
#### Auth Server: port 8001
#### Resource Server: port 8002
```
./run_servers.sh
```
