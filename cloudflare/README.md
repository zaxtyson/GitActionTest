# CloudFlare

## Use Worker

- Create `Service`
- Put the `proxy.js` into online editor
- Save & Deploy

## Problems

- [Worker cannot connect to custom port](https://community.cloudflare.com/t/worker-cannot-connect-to-custom-port/173996)

## Solution

- Start the repo update service listen on `8086`
- Add a reverse proxy for this port

```
Git Action Runner ==> https://repo.zaxtyson.workers.dev  ==>
CloudFlare Worker ==> http://repo-proxy.zaxtyson.cn  ==>
Nginx Reverse Proxy ==> http://zaxtyson.cn:8086
```