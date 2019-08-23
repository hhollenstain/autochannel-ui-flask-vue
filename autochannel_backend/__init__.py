"""
init - version info
"""
from flask import abort, redirect, request, session 
from requests_oauthlib import OAuth2Session
from functools import wraps

VERSION_INFO = (0, 0, 1)
VERSION = '.'.join(str(c) for c in VERSION_INFO)

def is_authenticated():
  return session.get('oauth2_token')

def login_required(view):
  @wraps(view)
  def view_wrapper(*args, **kwargs):
    if is_authenticated():
      return view(*args, **kwargs)
    else:
      return redirect('/api/login')
  return view_wrapper