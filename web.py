from typing import Optional
from fastapi import FastAPI, responses, Response
from fastapi.param_functions import Cookie
import requests
from pydantic import BaseModel
import os

app = FastAPI()
consumer_key = os.environ.get("pocket_consumer_key")


class Data(BaseModel):
    text: str


@app.get("/auth_success")
def root(response: Response, code: Optional[str] = Cookie(None)):
    url = "https://getpocket.com/v3/oauth/authorize"
    json_payload = {"consumer_key": consumer_key, "code": code}
    json_response = requests.post(
        url, json_payload, headers={"x-Accept": "application/json"}
    ).json()

    username = json_response.get("username")
    access_token = json_response.get("access_token")

    res = responses.JSONResponse({"message": json_response})

    res.set_cookie("username", username, max_age=10000)
    res.set_cookie("access_token", access_token, max_age=10000)

    return res


@app.get("/items")
def test(access_token: Optional[str] = Cookie(None)):
    if access_token:
        url = "https://getpocket.com/v3/get"
        json_payload = {"access_token": access_token, "consumer_key": consumer_key}
        json_response = requests.post(
            url, json_payload, headers={"x-Accept": "application/json"}
        ).json()
    else:
        return responses.RedirectResponse("/")
    return {"ok": json_response}


@app.get("/")
def get_code(response: Response):
    retrieve_url = "https://getpocket.com/v3/oauth/request"
    json_payload = {
        "consumer_key": consumer_key,
        "redirect_uri": "http://127.0.0.1:8000/auth_success",
    }

    json_response = requests.post(
        retrieve_url, json=json_payload, headers={"x-Accept": "application/json"}
    )

    code = json_response.json().get("code")

    url = f"https://getpocket.com/auth/authorize?request_token={code}&redirect_uri={json_payload['redirect_uri']}"
    res = responses.RedirectResponse(url)
    res.set_cookie(key="code", value=code, max_age=1000)

    return res
