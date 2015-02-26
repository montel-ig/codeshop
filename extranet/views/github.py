# python
import hmac
import json

# django
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

# extranet
from extranet.models import Repository


@csrf_exempt
def webhook(request, extra_path):

    content_type = request.META.get('CONTENT_TYPE')
    assert(request.method == 'POST' and content_type == "application/json")

    github_digest = request.META.get('HTTP_X_HUB_SIGNATURE')
    my_digest = hmac.new(settings.GITHUB_WEBHOOKS_SECRET,
                         msg=request.body).hexdigest()

    # TODO: should use hmac.compare_digest with Python > 2.7.7
    assert(github_digest == my_digest)

    repo = Repository.objects.try_to_get_by_name(
        json.loads(request.body)['repository']['full_name']
    )
    repo._sync()
