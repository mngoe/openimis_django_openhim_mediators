from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json
import requests
from datetime import datetime
from openhim_mediator_utils.main import Main
from overview.models import configs
from overview.views import configview
from requests.auth import HTTPBasicAuth

@api_view(['GET'])
def getClaims(request):
	result = configview()
	configurations = result.__dict__
	data = requests.get(configurations["data"]["openimis_url"]+'Claim/',auth=HTTPBasicAuth(configurations["data"]["openimis_user"],configurations["data"]["openimis_passkey"]))
	if data.status_code == 200:
		res=data.json()
		resp = requests.post(configurations["data"]["sosys_url"]+'/claims/openimis_claims/',json=res['entry'])
		if resp.status_code == 200:
			return Response(resp.json())
		else:
			return Response({"Success":"Successfully sent claims"})
	else:
		return Response({"Error":"Failed to connect to openimis server with error code {}".format(data.status_code)})

def registerClaimsMediator():
	result = configview()
	configurations = result.__dict__
	API_URL = configurations["data"]["openhim_url"]+':'+str(configurations["data"]["openhim_port"])
	USERNAME = configurations["data"]["openhim_user"]
	PASSWORD = configurations["data"]["openhim_passkey"]

	options = {
	'verify_cert': False,
	'apiURL': API_URL,
	'username': USERNAME,
	'password': PASSWORD,
	'force_config': False,
	'interval': 10,
	}

	conf = {
	"urn": "urn:mediator:python_fhir_r4_claim_mediator",
	"version": "1.0.1",
	"name": "Python Fhir R4 Claim Mediator",
	"description": "Python Fhir R4 Claim Mediator",

	"defaultChannelConfig": [
		{
			"name": "Python Fhir R4 Claim Mediator",
			"urlPattern": "^/Claim$",
			"routes": [
				{
					"name": "Python Fhir R4 Claim Mediator Route",
					"host": configurations["data"]["mediator_url"],
					"path": "/Claim",
					"port": configurations["data"]["mediator_port"],
					"primary": True,
					"type": "http"
				}
			],
			"allow": ["admin"],
			"methods": ["GET", "POST"],
			"type": "http"
		}
	],

	"endpoints": [
		{
			"name": "Python Fhir R4 Claim Mediator",
			"host": configurations["data"]["mediator_url"],
			"path": "/Claim",
			"port": configurations["data"]["mediator_port"],
			"primary": True,
			"type": "http"
		}
	]
	}
	openhim_mediator_utils = Main(
		options=options,
		conf=conf
		)
	openhim_mediator_utils.register_mediator()
	checkHeartbeat(openhim_mediator_utils)
def checkHeartbeat(openhim_mediator_utils):
	openhim_mediator_utils.activate_heartbeat()
