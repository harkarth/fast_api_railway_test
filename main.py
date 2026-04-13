from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()


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
	</style>
</head>
<body>
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
	</style>
</head>
<body>
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
