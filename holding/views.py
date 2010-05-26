from whatever.models import Prediction
from forms import WaitingListForm

from utils import render
from utils import getThisYear
from utils import _parseFeed

# should use django cache but was gettig recursion errors
# on the live server only.  ?!?!
CACHE = {}
CACHE_COUNT = 0


@render('holding.html')
def home(request):
    if request.method == 'POST':
        waiting = WaitingListForm(request.POST)
        if waiting.is_valid():
            item = waiting.save()
            item.save()
            message = "Thanks. We'll let you know when the new game starts!"
        else:
            message = "That's not a valid email address"
    blog_date, blog_title, blog_content = _parseFeed()
    this_year = getThisYear()
    predictions = Prediction.objects.filter(year=this_year)
    predictions = predictions.order_by('-score', '-goaldiff', 'created_date')
    predictions = predictions.all()[:10]
    return locals()

@render('holding2.html')
def home2(request):
    if request.method == 'POST':
        waiting = WaitingListForm(request.POST)
        if waiting.is_valid():
            item = waiting.save()
            item.save()
            message = "Thanks. We'll let you know when the new game starts!"
        else:
            message = "That's not a valid email address"
    blog_date, blog_title, blog_content = _parseFeed()
    this_year = getThisYear()
    return locals()


