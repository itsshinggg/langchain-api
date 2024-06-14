# Langchain-API

## Launching an Ubuntu EC2 Instance on AWS

### Pre-requisites

1. **Obtain an Elastic IP Address**:

   - Go to the [AWS Management Console](https://aws.amazon.com/console/).
   - Navigate to the EC2 Dashboard.
   - Click on "Elastic IPs" under the "Network & Security" section.
   - Allocate a new Elastic IP address and attach it to your EC2 instance.

2. **Obtain Your Own Domain**:

   - Register a domain name through a domain registrar (e.g., Namecheap, GoDaddy, AWS Route 53).
   - Point the domain to your Elastic IP address through the DNS settings of your domain registrar.

3. **Obtain OpenAI API Secret Key**:
   - Sign up or log in to your account on the [OpenAI website](https://beta.openai.com/).
   - Navigate to the API keys section.
   - Generate a new API key and copy the secret key for later use.

### EC2 Setup

These steps can be included in the EC2's user data for automatic execution on launch.

#### Install Packages and Clone the GitHub Repository

1. Update the package list:

   ```bash
   sudo apt-get update
   ```

2. Install Python, pip, virtual environment, and Git:

   ```bash
   sudo apt install python3-pip python3-venv git -y
   ```

3. Clone the GitHub repository:
   ```bash
   sudo git clone https://github.com/itsshinggg/langchain-api.git
   ```

#### Install Nginx and Set Up Reverse Proxy

1. Install Nginx:

   ```bash
   sudo apt install nginx
   ```

2. Modify the Nginx configuration file:

   ```bash
   sudo nano /etc/nginx/sites-available/default
   ```

3. Update the config file as shown below (replace `<domainname.com>`, `<ELASTIC-IP>`, and `<PORT>` with your actual values):

   ```nginx
   server {
       server_name <domainname.com>;

       location / {
           proxy_pass http://<ELASTIC-IP>:<PORT>;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }

       listen 80;
   }

   server {
       if ($host = <domainname.com>) {
           return 301 http://$host$request_uri;
       }
   }
   ```

4. Test the Nginx configuration:

   ```bash
   sudo nginx -t
   ```

5. Restart Nginx:
   ```bash
   sudo service nginx restart
   ```

#### Obtain SSL Certificates and Update Nginx Configuration

1. Install Certbot for SSL:

   ```bash
   sudo snap install --classic certbot
   ```

2. Obtain SSL certificates with Certbot:

   ```bash
   sudo certbot --nginx -d <domainname.com>
   ```

3. If the SSL gets obtained successfully, the config file should look like below (replace `<domainname.com>` with your actual value):

   ```nginx
   server {
       server_name <domainname.com>;

       location / {
           proxy_pass http://<ELASTIC-IP>:<PORT>;
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

   server {
       if ($host = <domainname.com>) {
           return 301 https://$host$request_uri;
       } # managed by Certbot
   }
   ```

4. Test the Nginx configuration:

   ```bash
   sudo nginx -t
   ```

5. Restart Nginx:
   ```bash
   sudo service nginx restart
   ```

#### Verifying Certbot Auto-Renewal

6. Check the status of the Certbot auto-renewal service:
   ```bash
   sudo systemctl status snap.certbot.renew.service
   ```

## Setting Up the Python Environment

1. Change directory to the project folder:

   ```bash
   cd langchain-api/
   ```

2. Create a virtual environment:

   ```bash
   python3 -m venv <new-virtual-environment-name>
   ```

3. Activate the virtual environment:

   ```bash
   source <new-virtual-environment-name>/bin/activate
   ```

4. Change ownership of the virtual environment directory (if needed):

   ```bash
   sudo chown -R ubuntu:ubuntu <new-virtual-environment-name>
   ```

5. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

6. Create a `.env` file and store your OpenAI API key in it:
   ```bash
   echo "OPENAI_API_KEY=your-key" > .env
   ```

## Running the Application

1. Run the application:
   ```bash
   python3 -m uvicorn main:app --host 0.0.0.0 --port <port-number>
   ```

---

Replace placeholders like `<domainname.com>`, `<ELASTIC-IP>`, `<PORT>`, `<new-virtual-environment-name>`, and `<port-number>` with your actual values.
