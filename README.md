# Flask webserver for my personal website

No one will need to run this, I don't even need these notes... But in the name of documentation here is how to start up the webserver


### Running locally
```
# navigate to the root directory
cd resume-website

# create virtualenv and activate it
python -m venv venv && source ./venv/bin/activate

# install deps
pip install -r ./requirements.txt

# run this command in the root directory
flask run
```

### Nginx + uWSGI hosting config
```
# for the nginx config (not including ssl certbot lines)
server {
    ...

    listen 443 ssl;
    server_name coredumped.info;

    location / {
        proxy_pass http://127.0.0.1:<PORT>/;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Prefix /;
    }
}

# command for the uwsgi service
uwsgi --http 127.0.0.1:<PORT> --master -p <CPU# * 2> -w wsgi:app
```
