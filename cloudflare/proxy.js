addEventListener("fetch", event => {
    event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
    const cf_worker_host = "https://repo.zaxtyson.workers.dev"
    const repo_host = "http://repo-proxy.zaxtyson.cn"   // only support port 80/443
    const url = request.url.replace(cf_worker_host, repo_host)

    const req = new Request(url, {
        method: request.method,
        body: request.body,
        headers: request.headers
    })

    return fetch(req)
}