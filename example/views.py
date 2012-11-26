from django.http import (HttpResponse)

def home(request):
    return HttpResponse("This is just a simple test page.  You found it via the url <pre>%s</pre>"
                        % request.path_info)
