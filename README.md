# langchain-api

lauch ubuntu EC2 instance on AWS

set up (these can be included in a EC2's user data)

install packages and clone the github repository

1. `sudo apt-get update`
2. `sudo apt install python3-pip python3-venv git -y`
3. `sudo git clone https://github.com/itsshinggg/langchain-api.git`

install nginx, set reverse proxy, and obtain SSL

1. `sudo apt install nginx`
2. `sudo snap install --classic certbot`
3. `sudo nano /etc/nginx/sites-available/default`
4. modify the config file to below

   ```
   server {
        server_name <domainname.com>;

        location / {
        proxy_pass <ELASTIC-IP>:<PORT>;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        }

      listen [::]:443 ssl ipv6only=on; # managed by Certbot
      listen 443 ssl; # managed by Certbot
      ssl_certificate /etc/letsencrypt/live/<domainname.com>/fullchain.pem; # managed by Certbot
      ssl_certificate_key /etc/letsencrypt/live/<domainname.com>/privkey.pem; # managed by Certbot
      include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
      ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
   }
   ```

5. `sudo nginx -t`
6. `sudo certbot --nginx -d <domainname.com> `

Verifying Certbot Auto-Renewal

7. `sudo systemctl status snap.certbot.renew.service`
8. `sudo service nginx restart`

---

create your python virtual environemnt and activate it

1. `cd langchain-api/`
2. `python3 -m venv <new virtual environment name>`
3. `source <your virtual environment name>/bin/activate`

install required packages in the virtual environment

4. `sudo chown -R ubuntu:ubuntu <your virtual environment name>`
5. `pip install -r requirements.txt`
6. create .env file and store openai api key to it (OPENAI_API_KEY=your-key)

run

7. `python3 -m uvicorn main:app --host 0.0.0.0 --port number`

---
