# -*- encoding:utf-8 -*-
# Create your views here.
import os
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson as json
from django.conf import settings
from readxls import resolv

import logging
logger = logging.getLogger(__name__)

def handle_uploaded_file(f, default_path='uploads'):
    logger.debug("handle_uploaded_file: {}".format(f))
    try:
        if f:
            path = os.path.join(settings.MEDIA_ROOT, default_path)
            if not os.path.isdir(path):
                os.makedirs(path)
            ext = f.name.split('.')[-1]
            file_name = "file.xls"
            path_file = os.path.join(path,file_name)
            if ext in ['jpg', 'jpeg', 'png', 'gif']:
                parser = ImageFile.Parser()
                for chunk in f.chunks():
                    parser.feed(chunk)
                img = parser.close()
                try:
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    img.save(path_file, 'jpeg',quality=100)
                except:
                    return False, "", ""
            else:
                with open(path_file, "wb+") as fn:
                    for chunk in f.chunks():
                        fn.write(chunk)
                out_file, form, origin_form = resolv(path_file)
            logger.debug('handle_uploaded_file name:{} size {} write as {}'.format(f.name, f.size, path_file))
            return True, out_file, os.path.join(settings.STATIC_URL, "media/%s/%s" % (default_path, out_file)), form, origin_form
    except Exception as e:
        logger.debug(e)
    return False, "", ""

def _upload_xls(request):
    '''
           文件上传POST请求
    '''
    logger.debug('enter CVFile POST view... {}'.format(request.user))

    logger.debug('upload_view POST request.FILES {} user {}'.format(request.FILES, request.user))
    print('upload_view POST request.FILES {} user {}'.format(request.FILES, request.user))
    file1 = request.FILES.get('file')
    # import pdb;pdb.set_trace()
    ret,file_name, file_url, form, origin_form = handle_uploaded_file(file1, "uploads/xls")

    # if os.path.exists(file_name):

    # return HttpResponse(json.dumps(file_url), mimetype='application/json')
    ctx = dict()
    ctx['file_name'] = file_name
    ctx['file_url'] = file_url
    ctx['form'] = form
    ctx['origin_form'] = origin_form
    return render_to_response("xls/xls_download.html", ctx, context_instance=RequestContext(request))

@csrf_exempt
def upload_xls(request):
    '''
    上传xls
    '''

    if request.method == 'GET':
        ctx = dict()
        ctx['xls_url'] = 'uploads/xls/file.xls'
        return render_to_response('xls/xls_upload.html',ctx,context_instance=RequestContext(request))
    if request.method != 'POST':
        logger.warn('unsupported in image_view method {}'.format(request.method))
        return HttpResponseForbidden(json.dumps('unsupported request method {}'.format(request.method)),
                mimetype="application/json")
    return _upload_xls(request)
