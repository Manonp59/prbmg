from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader

def index(request):
    data_points = [
        { "label": "apple",  "y": 10  },
        { "label": "orange", "y": 15  },
        { "label": "banana", "y": 25  },
        { "label": "mango",  "y": 30  },
        { "label": "grape",  "y": 28  }
    ]
    return render(request, 'index.html', { "data_points" : data_points })