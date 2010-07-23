# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 UNINETT AS
#
# This file is part of Network Administration Visualized (NAV).
#
# NAV is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License version 2 as published by the Free
# Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.  You should have received a copy of the GNU General Public License
# along with NAV. If not, see <http://www.gnu.org/licenses/>.
#

from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

from nav.django.utils import get_verbose_name
from nav.web.message import new_message, Messages

def group_query(qs, identifier):
    objects = {}
    for object in qs:
        if object[identifier] not in objects:
            objects[object[identifier]] = []
        objects[object[identifier]].append(object)
    return objects

def move(request, model, form_model, redirect, title_attr='id'):
    data = None
    confirm = False
    objects = model.objects.filter(id__in=request.POST.getlist('object'))

    if request.POST.get('preview'):
        form = form_model(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            confirm = True
    elif request.POST.get('save'):
        form = form_model(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            objects.update(**data)
            new_message(request._req, "M-M-M-M-Monster kill", Messages.SUCCESS)
            return HttpResponseRedirect(reverse(redirect))
    else:
        form = form_model()

    fields = form.fields.keys()
    values = objects.values('pk', title_attr, *fields)
    object_list = []
    attr_list = [title_attr] + fields
    for object in values:
        row = {
            'pk': object['pk'],
            'values': [("Current %s" % attr, object[attr]) for attr in attr_list],
        }
        if data:
            new_values = [("New %s" % attr, data[attr]) for attr in fields]
            row['values'].extend(new_values)
        object_list.append(row)

    context = {
        'form': form,
        'objects': objects,
        'values': object_list,
        'data': data,
        'confirm': confirm,
    }
    return render_to_response('seeddb/move.html',
        context, RequestContext(request))
