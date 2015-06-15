import re
from django.http import HttpResponse,JsonResponse,Http404
from django.shortcuts import render
import requests
# Create your views here.
from django.views.decorators.csrf import csrf_exempt


def welcome(request):
    return HttpResponse("Welcome!!")


@csrf_exempt
def greetings(request):
    if request.GET:
        if not request.GET['q']:
            raise Http404()
        else:
            s = request.GET['q']
            if s.startswith('Hi!') or s.startswith('Hello!') or s.startswith('Good morning!') or s.startswith('Good evening!') or s.startswith('Good night!') :
                return JsonResponse({'answer':'Hello, Kitty! Whoever is watching this is a genius!!',})
            else:
                raise Http404()

    raise Http404()



def get_weather_data(city):
    try:
        ret = requests.get('http://api.openweathermap.org/data/2.5/weather?q='+city)
        d = ret.json()

        if d['cod'] != 200:
            raise Http404()
        return d
    except Exception,e:
        raise Http404()

@csrf_exempt
def weather(request):
    if request.GET:
        if not request.GET['q']:
            raise Http404()
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
                    raise Http404()
            elif s.startswith('What is today\'s humidity in ') and s.endswith('?'):
                ret = re.match(r'^What is today\'s humidity in (?P<city>.*)\?$',s)
                if ret:
                    city = ret.group('city')
                    data = get_weather_data(city)
                    humidity = data['main']['humidity']
                    return JsonResponse({'answer':humidity})
                else:
                    raise Http404()
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
                    raise Http404()
            else:
                raise Http404()

    raise Http404()



@csrf_exempt
def query(request):
    return HttpResponse("query")