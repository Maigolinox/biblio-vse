# Trying out a new interface someone asked me for yesterday in the hallway
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views import View
def render_new_dashboard():
    return "Dashboard V2"
