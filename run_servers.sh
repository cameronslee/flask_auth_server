#!/bin/bash

cd auth
python auth_server.py &
cd ..

cd client
python client_server.py &
cd ..

cd resource
python resource_server.py &
cd ..