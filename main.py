import hashlib
import ipaddress
import os
import secrets

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse

ALLOWED_IPS = os.environ["ALLOWED_IPS"].split(",")
AUTH_USERNAME = os.environ["AUTH_USERNAME"]
AUTH_PASSWORD_HASH = hashlib.sha256(os.environ["AUTH_PASSWORD"].encode()).hexdigest()

PRIVATE_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
]

sessions: set[str] = set()

app = FastAPI(docs_url=None, redoc_url=None)


def is_allowed(ip: str) -> bool:
    if ip in ALLOWED_IPS:
        return True
    try:
        addr = ipaddress.ip_address(ip)
        return any(addr in net for net in PRIVATE_NETWORKS)
    except ValueError:
        return False


@app.middleware("http")
async def auth_and_ip_middleware(request: Request, call_next):
    client_ip = (
        request.headers.get("x-forwarded-for", request.client.host)
        .split(",")[0]
        .strip()
    )
    if not is_allowed(client_ip):
        return Response(status_code=403, content="Forbidden")
    auth = request.cookies.get("session")
    if auth not in sessions:
        if request.url.path == "/login" and request.method == "POST":
            return await call_next(request)
        return HTMLResponse(
            status_code=401,
            content="""
<!DOCTYPE html>
<html>
<head>
	<title>Login</title>
	<style>
		body {
			display: flex;
			justify-content: center;
			align-items: center;
			height: 100vh;
			margin: 0;
			font-family: sans-serif;
		}
		.container { text-align: center; }
		input {
			padding: 10px;
			font-size: 16px;
			width: 250px;
			margin-bottom: 10px;
		}
		button {
			padding: 10px 24px;
			font-size: 16px;
			cursor: pointer;
		}
	</style>
</head>
<body>
	<div class="container">
		<h1>Login</h1>
		<form action="/login" method="post">
			<input type="text" name="username" placeholder="Username" required><br>
			<input type="password" name="password" placeholder="Password" required><br>
			<button type="submit">Login</button>
		</form>
	</div>
</body>
</html>
""",
        )
    return await call_next(request)


@app.post("/login")
async def login(request: Request):
    form = await request.form()
    username = form.get("username", "")
    password = form.get("password", "")
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if username == AUTH_USERNAME and password_hash == AUTH_PASSWORD_HASH:
        token = secrets.token_hex(32)
        sessions.add(token)
        response = HTMLResponse(
            content='<meta http-equiv="refresh" content="0; url=/">'
        )
        response.set_cookie("session", token, httponly=True)
        return response
    return HTMLResponse(
        status_code=401, content="<h1>Invalid credentials</h1><a href='/'>Try again</a>"
    )


@app.get("/logout")
async def logout(request: Request):
    token = request.cookies.get("session")
    if token and token in sessions:
        sessions.discard(token)
    response = HTMLResponse(content='<meta http-equiv="refresh" content="0; url=/">')
    response.delete_cookie("session")
    return response


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(
        content="""
<!DOCTYPE html>
<html>
<head>
	<title>FastAPI WebUI</title>
	<style>
		body {
			display: flex;
			justify-content: center;
			align-items: center;
			height: 100vh;
			margin: 0;
			font-family: sans-serif;
		}
		.container {
			text-align: center;
		}
		input[type="text"] {
			padding: 10px;
			font-size: 16px;
			width: 300px;
			margin-bottom: 10px;
		}
		button {
			padding: 10px 24px;
			font-size: 16px;
			cursor: pointer;
		}
		.logout {
			position: fixed;
			top: 10px;
			right: 10px;
		}
	</style>
</head>
<body>
	<a class="logout" href="/logout">Logout</a>
	<div class="container">
		<h1>Enter some text</h1>
		<form action="/submit" method="post">
			<input type="text" name="text" placeholder="Type something..." required><br>
			<button type="submit">Submit</button>
		</form>
	</div>
</body>
</html>
"""
    )


@app.post("/submit")
async def submit(request: Request):
    form = await request.form()
    text = form.get("text", "")
    print(text)
    return HTMLResponse(
        content=f"""
<!DOCTYPE html>
<html>
<head>
	<title>FastAPI WebUI</title>
	<style>
		body {{
			display: flex;
			justify-content: center;
			align-items: center;
			height: 100vh;
			margin: 0;
			font-family: sans-serif;
		}}
		.container {{
			text-align: center;
		}}
		input[type="text"] {{
			padding: 10px;
			font-size: 16px;
			width: 300px;
			margin-bottom: 10px;
		}}
		button {{
			padding: 10px 24px;
			font-size: 16px;
			cursor: pointer;
		}}
		.logout {{
			position: fixed;
			top: 10px;
			right: 10px;
		}}
	</style>
</head>
<body>
	<a class="logout" href="/logout">Logout</a>
	<div class="container">
		<h1>Enter some text</h1>
		<form action="/submit" method="post">
			<input type="text" name="text" placeholder="Type something..." required><br>
			<button type="submit">Submit</button>
		</form>
		<p>You submitted: <strong>{text}</strong></p>
	</div>
</body>
</html>
"""
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", port=8005, reload=True)
