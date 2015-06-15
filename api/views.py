import re
from django.http import HttpResponse,JsonResponse,Http404,HttpResponseBadRequest
from django.shortcuts import render
import requests
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
import json

def welcome(request):
    return HttpResponse("Welcome!!")


@csrf_exempt
def greetings(request):
    if request.GET:
        if not request.GET['q']:
            return HttpResponseBadRequest()
        else:
            s = request.GET['q']
            if s.startswith('Hi!') or s.startswith('Hello!') or s.startswith('Good morning!') or s.startswith('Good evening!') or s.startswith('Good night!') :
                return JsonResponse({'answer':'Hello, Kitty! Whoever is watching this is a genius!!',})
            else:
                return HttpResponseBadRequest()

    return HttpResponseBadRequest()



def get_weather_data(city):
    try:
        ret = requests.get('http://api.openweathermap.org/data/2.5/weather?q='+city)
        d = ret.json()

        if d['cod'] != 200:
            return HttpResponseBadRequest()
        return d
    except Exception,e:
        raise Http404()


@csrf_exempt
def weather(request):
    if request.GET:
        if 'q' not in request.GET.keys():
            return HttpResponseBadRequest()
        else:
            s = request.GET['q']
            if s.startswith('What is today\'s temperature in ') and s.endswith('?'):
                ret = re.match(r'^What is today\'s temperature in (?P<city>.*)\?$',s)
                if ret:
                    city = ret.group('city')
                    data = get_weather_data(city)
                    temp = '%d K' % (data['main']['temp'],)
                    return JsonResponse({'answer':temp})
                else:
                    return HttpResponseBadRequest()
            elif s.startswith('What is today\'s humidity in ') and s.endswith('?'):
                ret = re.match(r'^What is today\'s humidity in (?P<city>.*)\?$',s)
                if ret:
                    city = ret.group('city')
                    data = get_weather_data(city)
                    humidity = data['main']['humidity']
                    return JsonResponse({'answer':humidity})
                else:
                    return HttpResponseBadRequest()
            elif 'weather' in s:
                ret = re.match(r'^Is there (?P<condition>(Rain|Clouds|Clear)) weather today in (?P<city>.*)\?$',s)
                if ret:
                    condition = ret.group('condition')
                    city = ret.group('city')
                    data = get_weather_data(city)
                    # print data['weather'][0]['main']
                    if data['weather'][0]['main']==condition:
                        return JsonResponse({'answer':'Yes',})
                    else:
                        return JsonResponse({'answer':'No',})
                else:
                    return HttpResponseBadRequest()
            else:
                return HttpResponseBadRequest()

    return HttpResponseBadRequest()



@csrf_exempt
def query(request):
    if request.GET and 'question' in request.GET.keys():
        quest = request.GET['question']
        ret = requests.get("http://quepy.machinalis.com/engine/get_query",params={'question':quest})
        if ret.status_code != requests.codes.ok:
            return JsonResponse({'answer':'Your majesty! Jon Snow knows nothing! So do I!'})
        # print ret.content
        data = json.loads(str(ret.content))
        # data = ret.content
        q = data['queries'][0]['query']
        if not q:
            return JsonResponse({'answer':'Your majesty! Jon Snow knows nothing! So do I!'})
        payload = {'debug':'on',
                   'timeout':'3000',
                   'query':q,
                   'default-graph-uri':'',
                   'format':'application/sparql-results+json',
                   }
        db_ret = requests.get("http://dbpedia.org/sparql",params=payload)
        if db_ret.status_code!=requests.codes.ok:
            return JsonResponse({'answer':'Your majesty! Jon Snow knows nothing! So do I!'})
        # print db_ret.content
        data = json.loads(db_ret.content)
        var_name = data['head']['vars'][0]
        res = data['results']['bindings']
        for var_name in data['head']['vars']:
            for x in res:
                if x[var_name]['xml:lang'] == 'en' :
                    return JsonResponse({'answer':x[var_name]['value']})

        return JsonResponse({'answer':'Your majesty! Jon Snow knows nothing! So do I!'})
    else:
        return HttpResponseBadRequest()
