# python
import hashlib
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

    type_, github_digest = request.META.get('HTTP_X_HUB_SIGNATURE').split('=')
    assert(type_ == 'sha1')

    my_digest = hmac.new(settings.GITHUB_WEBHOOKS_SECRET,
                         request.body,
                         hashlib.sha1).hexdigest()

    if hasattr(hmac, 'compare_digest'):  # Python > 2.7.7
        assert(hmac.compare_digest(github_digest, my_digest))
    else:
        assert(github_digest == my_digest)

    repo = Repository.objects.try_to_get_by_name(
        json.loads(request.body)['repository']['full_name']
    )
    repo._sync()
