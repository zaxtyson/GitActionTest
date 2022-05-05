# GitActionTest

Build dep & rpm packages for Ubuntu、Debian、Centos、Redhat


## Repo Update Server

- Require python version >= 3.7
- Repo update service runs on `8086`

```
pip3 install sanic
python3 app.py
```

## Proxy

Slow😣: `Git Action Runner` == PUT ==> `Repo Server`

Fast⚡: `Git Action Runner` == PUT ==> `Cloudflare Worker` == PUT ==> `Repo Server`