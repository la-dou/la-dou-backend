#web: uvicorn main:app --port 8080
#https://dev.to/mrcartoonster/fastapi-do-deploy-1h10
web: gunicorn --worker-tmp-dir /dev/shm --config gunicorn.conf.py main:app la-dou.wsgi
