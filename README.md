# langchain-api

1. lauch ubuntu EC2 instance on AWS

set up (these can be included in a EC2's user data)

2. `sudo apt-get update`
3. `sudo apt install python3-pip`
4. `sudo apt install python3-venv -y`
5. `sudo apt install git`
6. `sudo git clone https://github.com/itsshinggg/langchain-api.git`
-----

7. `cd langchain-api/`

create your python virtual environemnt and activate it
9. `python3 -m venv <your virtual environment name>`
10. `source <your virtual environment name>/bin/activate`

enable a permission and download required packages
11. `sudo chown -R ubuntu:ubuntu <your virtual environment name>`
12. `pip install -r requirements.txt`
13. store openai api key into .env file

run  `python3 -m uvicorn main:app --host 0.0.0.0 --port 8000`
