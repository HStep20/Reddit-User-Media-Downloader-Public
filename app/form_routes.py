from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
import app.reddit_media_downloader_core as rmdc

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def read_form():
    return "hello world"


@app.get("/form")
def form_post(request: Request):
    result = "Type a number"
    return templates.TemplateResponse(
        "form.html", context={"request": request, "username": result}
    )


@app.post("/form")
def form_post(
    request: Request,
    username: str = Form(),
    subreddit: str = Form(None),
    start_date=Form(None),
    end_date=Form(None),
    post_limit: int = Form(100),
):
    rmdc.main(username, subreddit, post_limit)
    return templates.TemplateResponse(
        "form.html",
        context={
            "request": request,
            "username": username,
            "start_date": start_date,
            "end_date": end_date,
            "post_limit": post_limit,
        },
    )
