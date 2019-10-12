#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import create_ctfd, destroy_ctfd, gen_user


def test_ctfd_setup_redirect():
    """Test that a fresh CTFd instance redirects to /setup"""
    app = create_ctfd(setup=False)
    with app.app_context():
        with app.test_client() as client:
            r = client.get("/users")
            assert r.status_code == 302
            assert r.location == "http://localhost/setup"

            # Files in /themes load properly
            r = client.get("/themes/core/static/css/main.css")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_ctfd_setup_verification():
    app = create_ctfd(setup=False)
    with app.app_context():
        with app.test_client() as client:
            r = client.get("/setup")
            assert r.status_code == 200

            with client.session_transaction() as sess:
                data = {
                    "ctf_name": "CTFd",
                    "name": "test",
                    "email": "test@ctfd.io",
                    "password": "",
                    "user_mode": "users",
                    "nonce": sess.get("nonce"),
                }
            r = client.post("/setup", data=data)
            assert "longer password" in r.get_data(as_text=True)

            gen_user(app.db, name="test", email="test@ctfd.io")

            data["password"] = "password"
            r = client.post("/setup", data=data)
            resp = r.get_data(as_text=True)
            assert "email has already been used" in resp
            assert "name is already taken" in resp

            data["name"] = "admin"
            data["email"] = "admin@ctfd.io"
            r = client.post("/setup", data=data)
            assert r.status_code == 302
            assert r.location == "http://localhost/"
    destroy_ctfd(app)
