# elision-gpt-backend

## Setup
### Install Python
Install Python 3.10 from [here](https://www.python.org/downloads/). 

Or with brew:
```bash
brew install python@3.10    
```

### Set environment variables
Copy the `set-env.sh` file to the root of the project and run the following command:
```bash
source set-env.sh
```

### Create a virtual environment
```bash
python -m venv elision-gpt-venv
```

Activate the virtual environment:
```bash
source elision-gpt-venv/bin/activate
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run the backend
```bash
python app.py    
```

## Deployment
The backend is deployed on AWS using EC2 instances. The following steps are required to deploy the backend:

1. Create an EC2 instance with the following specifications:
    - Instance type: t4.small
    - AMI: Ubuntu
    - Security group: allow inbound traffic on port 22, 80 and 443
    - Tags: add a tag with the key "Name" and a value of "elision-gpt-backend"

2. SSH into the EC2 instance:
    ```bash
    ssh -i "path/to/your/key.pem" ubuntu@<public-ip-address>
    ```

3. SSH into the EC2 instance and run the following commands:
    ```bash
    sudo yum update -y
    sudo yum install -y python3.10 python3-pip
    ```

4. Clone the elision-gpt repository:
    ```bash
    git clone https://github.com/BrentEerlingenWork/elision-gpt-backend.git
    ```

5. Navigate to the elision-gpt-backend directory:
    ```bash
    cd elision-gpt/elision-gpt-backend
    ```

6. Create a virtual environment:
    ```bash
    python -m venv elision-gpt-venv
    ```

7. Add the environment variables to the.bashrc file:
    ```bash
    echo "export OPEN_AI_KEY=<your-open-ai-key>" >> .bashrc
    echo "export AWS_ACCESS_KEY_ID=<your-aws-access-key-id>" >> .bashrc
    echo "export AWS_SECRET_ACCESS_KEY=<your-aws-secret-access-key>" >> .bashrc
    echo "export AWS_REGION=eu-west-1" >> .bashrc
    echo "export ASTRA_CLIENT=<your-astra-client>" >> .bashrc
    echo "export ASTRA_DB_ENDPOINT=<your-astra-db-endpoint>" >> .bashrc
    ```

8. Activate the virtual environment:
    ```bash
    source elision-gpt-venv/bin/activate
    ```

9. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

10. Run the backend:
    ```bash
    python app.py    
    ``` 
    The backend should now be running on port 5000 and accessible at http://<aws-public-ip-address>:5000.


### Run the backend in the background

1. Install the gunicorn package:
    ```bash
    pip install gunicorn
    ```

2. Run the backend in the background, use the following command:
    ```bash
    nohup gunicorn --timeout 120 --workers 3 --bind 0.0.0.0:5000 app:app &
    ```

3. Check the status of the backend:
    ```bash
    ps aux | grep gunicorn
    ```
    The backend should now be running on port 5000 and accessible at http://<aws-public-ip-address>:5000.

### Set up SSL/TLS 
Setting up SSL requires nginx and certbot. Follow the steps below to set up SSL:

1. Install nginx:    
    ```bash
    sudo apt-get update
    sudo apt-get install nginx
    ```

2. Install certbot:    
    ```bash
    sudo apt-get install software-properties-common
    sudo add-apt-repository ppa:certbot/certbot
    sudo apt-get update
    sudo apt-get install certbot python3-certbot-nginx
    ```

3. Edit the nginx configuration file:
    ```bash
    sudo vim /etc/nginx/sites-available/elision-gpt-backend
    ```
    Add the following lines to the file:
    ```nginx
    server {
        listen 443 ssl;
        server_name <your-domain>;

        ssl_certificate /etc/nginx/ssl/selfsigned.crt;
        ssl_certificate_key /etc/nginx/ssl/selfsigned.key;

        location / {
            proxy_pass http://localhost:5000;  # Forwarding to Flask
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
    ```

4. Create a symbolic link to the nginx configuration file:
    ```bash
    sudo ln -s /etc/nginx/sites-available/elision-gpt-backend /etc/nginx/sites-enabled
    ```
5. Check the syntax of the nginx configuration file:
    ```bash
    sudo nginx -t 
    ```

6. Restart nginx:
    ```bash
    sudo systemctl restart nginx
    ```

7. Create a self signed SSL certificate:
    ```bash
    sudo mkdir -p /etc/nginx/ssl
    ```

    ```bash
    sudo openssl req -x509 -newkey rsa:2048 -keyout /etc/nginx/ssl/selfsigned.key -out /etc/nginx/ssl/selfsigned.crt -days 365
    ```

8. Start app in the background:
    ```bash
    nohup gunicorn --timeout 120 --workers 3 --bind 0.0.0.0:5000 app:app &
    ```

## Troubleshooting
