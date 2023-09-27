# Flask OAuth2.0 Server

Client Server: port 8000
Auth Server: port 8001
API Server: port 8002

# Setup

## Install Required Packages
Can setup venv using requirements.txt

## Install OpenSSL
| OS                    | Instructions                                                                |
|-----------------------|-----------------------------------------------------------------------------|
| Linux (Debian/Ubuntu) | `sudo apt-get install openssl`                                              |
| macOS                 | (with [Homebrew](https://brew.sh/) package manager)  `brew install openssl` |
| Windows               | See [here](https://wiki.openssl.org/index.php/Binaries) for instructions.   |

# TODO big ol bash script

## Generate Keys
### Generate Private Key (used to generate access tokens, stored in auth server)
openssl genrsa -out ../auth/private_key.pem 2048

### Generate Public Key (used to verify access tokens, stored in API and client servers)
openssl rsa -in ../auth/private_key.pem -pubout -outform PEM -out ../client/public_key.pem
openssl rsa -in ../auth/private_key.pem -pubout -outform PEM -out ../api/public_key.pem

## Setup DB
cd auth 
flask db-init

