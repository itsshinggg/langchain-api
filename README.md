# langchain-api

lauch ubuntu EC2 instance on AWS

set up (these can be included in a EC2's user data)

install packages and clone the github repository

1. `sudo apt-get update`
2. `sudo apt install python3-pip`
3. `sudo apt install python3-venv -y`
4. `sudo apt install git`
5. `sudo git clone https://github.com/itsshinggg/langchain-api.git`

install nginx and set proxy

1. `sudo apt install nginx`
2. `sudo nano /etc/nginx/sites-available/default`
3. Add the following to the location part of the server block

   ```
   location / {
   proxy_pass http://<ec2-instance elastic IP address>:<port number> #whatever port your app runs on
   proxy_http_version 1.1;
   proxy_set_header Upgrade $http_upgrade;
   proxy_set_header Connection 'upgrade';
   proxy_set_header Host $host;
   proxy_cache_bypass $http_upgrade;
   }
   ```

4. `sudo nginx -t`
5. `sudo service nginx restart`

---

create your python virtual environemnt and activate it

1. `cd langchain-api/`
2. `python3 -m venv <your virtual environment name>`
3. `source <your virtual environment name>/bin/activate`

install required packages in the virtual environment

4. `sudo chown -R ubuntu:ubuntu <your virtual environment name>`
5. `pip install -r requirements.txt`
6. store openai api key into .env file

run

7. `python3 -m uvicorn main:app --host 0.0.0.0 --port number`

---

Installing Free SSL using Certbot

1. create a domain

Installing Certbot

2. `sudo snap install core; sudo snap refresh core`
3. `sudo apt remove certbot`
4. `sudo snap install --classic certbot`

Confirming Nginx’s Configuration

5. `sudo ln -s /snap/bin/certbot /usr/bin/certbot`

edit the server line of nginx configuration

6. `server_name example.com www.example.com;`
7. `sudo nginx -t`
8. `sudo systemctl reload nginx`

Obtaining an FREE SSL Certificate

9. `sudo certbot --nginx -d app.example.com `

Verifying Certbot Auto-Renewal

10. `sudo systemctl status snap.certbot.renew.service`

```

```
