# -*- coding: utf-8 -*-
# Copyright (C) 2018 Freetech Solutions

# This file is part of OMniLeads

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

"""
Vistas para manejar CalificacionCliente y los Formularios asociados a la Gestion correspondiente
"""

from __future__ import unicode_literals

import json
import logging as logging_

from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.generic.edit import FormView, CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.decorators.csrf import csrf_exempt

from simple_history.utils import update_change_reason

from ominicontacto_app.forms import (CalificacionClienteForm, FormularioNuevoContacto,
                                     RespuestaFormularioGestionForm)
from ominicontacto_app.models import (
    Contacto, Campana, CalificacionCliente, AgenteProfile, RespuestaFormularioGestion,
    OpcionCalificacion, UserApiCrm)

from reportes_app.models import LlamadaLog


logger = logging_.getLogger(__name__)


class CalificacionClienteFormView(FormView):
    """
    Vista para la creacion y actualización de las calificaciones.
    Además actualiza los datos del contacto.
    """
    template_name = 'formulario/calificacion_create_update.html'
    context_object_name = 'calificacion_cliente'
    model = CalificacionCliente
    form_class = CalificacionClienteForm

    def get_info_telefonos(self, telefono):
        """Devuelve información sobre los contactos que tienen un número de teléfono
        en la BD
        """
        contactos_info = list(self.campana.bd_contacto.contactos.filter(telefono=telefono))
        return contactos_info

    def get_contacto(self, id_contacto):
        if id_contacto is not None:
            # TODO: Analizar en que caso puede no haber un contacto.
            # try:
            #     return self.campana.bd_contacto.contactos.get(pk=id_contacto)
            # except Contacto.DoesNotExist:
            #     return None
            return Contacto.objects.get(pk=id_contacto)
        return None

    def get_object(self):
        if self.contacto is not None:
            try:
                return CalificacionCliente.objects.get(
                    opcion_calificacion__campana=self.campana,
                    contacto_id=self.contacto.id)
            except CalificacionCliente.DoesNotExist:
                return None
        return None

    def _es_numero_privado(self, telefono):
        if not telefono:
            return False
        return not telefono.isdigit()

    def dispatch(self, *args, **kwargs):
        self.agente = self.request.user.get_agente_profile()
        id_contacto = None
        self.call_data = None
        call_data_json = 'false'
        if 'call_data_json' in kwargs:
            call_data_json = kwargs['call_data_json']
            self.call_data = json.loads(call_data_json)
            self.campana = Campana.objects.get(pk=self.call_data['id_campana'])
            telefono = self.call_data['telefono']
            if self.call_data['id_contacto']:
                id_contacto = self.call_data['id_contacto']
        else:
            self.campana = Campana.objects.get(pk=kwargs['pk_campana'])
            telefono = kwargs.get('telefono', False)

        if 'pk_contacto' in kwargs:
            id_contacto = kwargs['pk_contacto']
        self.contacto = self.get_contacto(id_contacto)

        if self._es_numero_privado(telefono):
            self.contacto = None
        elif telefono and self.contacto is None:
            # se dispara desde una llamada desde el webphone
            contacto_info = self.get_info_telefonos(telefono)
            len_contacto_info = len(contacto_info)
            if len_contacto_info == 0:
                self.contacto = None
            elif len_contacto_info == 1:
                self.contacto = contacto_info[0]
            else:
                return HttpResponseRedirect(
                    reverse('campana_contactos_telefono_repetido',
                            kwargs={'pk_campana': self.campana.pk,
                                    'telefono': telefono,
                                    'call_data_json': call_data_json}))
        self.object = self.get_object()

        self.url_sitio_externo = ''
        if self.campana.tiene_interaccion_con_sitio_externo and self.call_data is not None:
            self.url_sitio_externo = self.campana.sitio_externo.get_url_interaccion(self.agente,
                                                                                    self.campana,
                                                                                    self.contacto,
                                                                                    self.call_data)

        return super(CalificacionClienteFormView, self).dispatch(*args, **kwargs)

    def get_calificacion_form_kwargs(self):
        calificacion_kwargs = {'instance': self.object}
        if self.request.method == 'GET' and self.contacto is not None:
            calificacion_kwargs['initial'] = {'contacto': self.contacto.id}
        elif self.request.method == 'POST':
            calificacion_kwargs['data'] = self.request.POST
        return calificacion_kwargs

    def get_form(self, historico_calificaciones=False):
        kwargs = self.get_calificacion_form_kwargs()
        kwargs['historico_calificaciones'] = historico_calificaciones
        return CalificacionClienteForm(campana=self.campana, **kwargs)

    def get_contacto_form_kwargs(self):
        kwargs = {'prefix': 'contacto_form'}
        initial = {}
        if self.contacto is not None:
            kwargs['instance'] = self.contacto
        else:
            if 'call_data_json' in self.kwargs:
                initial['telefono'] = self.call_data['telefono']
            else:
                # TODO: Cuando las manuales vengan con call_data sacar esto
                initial['telefono'] = self.kwargs['telefono']

        kwargs['initial'] = initial

        if self.request.method == 'POST':
            kwargs['data'] = self.request.POST
        return kwargs

    def get_contacto_form(self):
        return FormularioNuevoContacto(bd_metadata=self.campana.bd_contacto.get_metadata(),
                                       **self.get_contacto_form_kwargs())

    def _formulario_llamada_entrante(self):
        """Determina si estamos en presencia de un formulario
        generado por una llamada entrante
        """
        tipo_llamada = None
        if self.call_data is not None:
            tipo_llamada = int(self.call_data['call_type'])
        llamada_entrante = (tipo_llamada == LlamadaLog.LLAMADA_ENTRANTE)
        return llamada_entrante

    def get(self, request, *args, **kwargs):
        formulario_llamada_entrante = self._formulario_llamada_entrante()

        contacto_form = self.get_contacto_form()
        calificacion_form = self.get_form(historico_calificaciones=formulario_llamada_entrante)

        return self.render_to_response(self.get_context_data(
            contacto_form=contacto_form,
            calificacion_form=calificacion_form,
            campana=self.campana,
            llamada_entrante=formulario_llamada_entrante,
            call_data=self.call_data,
            url_sitio_externo=self.url_sitio_externo))

    def post(self, request, *args, **kwargs):
        """
        Valida formulario de Contacto y de CalificacionCliente
        """
        contacto_form = self.get_contacto_form()
        calificacion_form = self.get_form()
        contacto_form_valid = contacto_form.is_valid()
        calificacion_form_valid = calificacion_form.is_valid()
        self.usuario_califica = request.POST.get('usuario_califica', 'false') == 'true'
        formulario_llamada_entrante = self._formulario_llamada_entrante()
        # cuando el formulario es generado por una llamada entrante y el usuario no desea
        # calificar al contacto, solo validamos el formulario del contacto, ya que el de
        # calificación permanece oculto (en las dos siguientes validaciones)
        if formulario_llamada_entrante and not self.usuario_califica and contacto_form_valid:
            return self.form_valid(contacto_form)
        if formulario_llamada_entrante and not self.usuario_califica and not contacto_form_valid:
            return self.form_invalid(contacto_form)
        if contacto_form_valid and calificacion_form_valid:
            return self.form_valid(contacto_form, calificacion_form)
        else:
            return self.form_invalid(contacto_form, calificacion_form)

    def _check_metadata_no_accion_delete(self, calificacion):
        """ En caso que sea una calificacion de no gestion elimina metadatacliente"""
        if calificacion.opcion_calificacion.tipo is OpcionCalificacion.NO_ACCION \
                and calificacion.get_venta():
            calificacion.get_venta().delete()

    def _obtener_call_id(self):
        if self.call_data is not None:
            return self.call_data.get('call_id')
        return None

    def _calificar_form(self, calificacion_form):
        self.object_calificacion = calificacion_form.save(commit=False)
        self.object_calificacion.set_es_venta()
        self.object_calificacion.callid = self._obtener_call_id()
        self.object_calificacion.agente = self.agente
        self.object_calificacion.contacto = self.contacto

        # TODO: Ver si hace falta guardar que es una llamada manual
        # El parametro manual no viene mas
        if self.object is None:
            es_calificacion_manual = 'manual' in self.kwargs and self.kwargs['manual']
            self.object_calificacion.es_calificacion_manual = es_calificacion_manual

        self.object_calificacion.save()
        # modificamos la entrada de la modificación en la instancia para así diferenciar
        # cambios realizados directamente desde una llamada de las otras modificaciones
        update_change_reason(self.object_calificacion, self.kwargs.get('from'))

        # Finalizar relacion de contacto con agente
        # Optimizacion: si ya hay calificacion ya se termino la relacion agente contacto antes.
        if self.campana.type == Campana.TYPE_PREVIEW and self.object is None:
            self.campana.gestionar_finalizacion_relacion_agente_contacto(self.contacto.id)

        # check metadata en calificaciones de no accion y eliminar
        self._check_metadata_no_accion_delete(self.object_calificacion)

        if self.object_calificacion.es_venta and \
                not self.campana.tiene_interaccion_con_sitio_externo:
            return redirect(self.get_success_url_venta())
        else:
            message = _('Operación Exitosa! '
                        'Se llevó a cabo con éxito la calificación del cliente')
            messages.success(self.request, message)
        if self.object_calificacion.es_agenda():
            return redirect(self.get_success_url_agenda())
        elif self.kwargs['from'] == 'reporte':
            return redirect(self.get_success_url_reporte())
        else:
            return redirect(self.get_success_url())

    def form_valid(self, contacto_form, calificacion_form=None):
        nuevo_contacto = False
        if self.contacto is None:
            nuevo_contacto = True
        self.contacto = contacto_form.save(commit=False)
        if nuevo_contacto:
            self.contacto.bd_contacto = self.campana.bd_contacto
        self.contacto.datos = contacto_form.get_datos_json()
        # TODO: OML-1016 Verificar bien que hacer aca o si ya se hizo
        if nuevo_contacto:
            self.contacto.es_originario = False
        self.contacto.save()
        if calificacion_form is not None:
            # el formulario de calificación no es generado por una llamada entrante
            return self._calificar_form(calificacion_form)
        else:
            # en el caso de una campaña entrante que el usuario no desea calificar
            message = _('Operación Exitosa! '
                        'Se llevó a cabo con éxito la creación del contacto')
            self.call_data['id_contacto'] = self.contacto.pk
            self.call_data['telefono'] = self.contacto.telefono
            url_calificar_llamada_entrante = reverse(
                'calificar_llamada', kwargs={'call_data_json': json.dumps(self.call_data)})
            messages.success(self.request, message)
            return redirect(url_calificar_llamada_entrante)

    def form_invalid(self, contacto_form, calificacion_form):
        """
        Re-renders the context data with the data-filled forms and errors.
        """
        return self.render_to_response(self.get_context_data(
            contacto_form=contacto_form,
            calificacion_form=calificacion_form,
            campana=self.campana,
            call_data=self.call_data,
            url_sitio_externo=self.url_sitio_externo)
        )

    def get_success_url_venta(self):
        return reverse('formulario_venta',
                       kwargs={"pk_calificacion": self.object_calificacion.id})

    def get_success_url_agenda(self):
        return reverse('agenda_contacto_create',
                       kwargs={"pk_campana": self.campana.id,
                               "pk_contacto": self.contacto.id})

    def get_success_url_reporte(self):
        return reverse('reporte_agente_calificaciones',
                       kwargs={"pk_agente": self.object_calificacion.agente.pk})

    def get_success_url(self):
        return reverse('recalificacion_formulario_update_or_create',
                       kwargs={"pk_campana": self.campana.id,
                               "pk_contacto": self.contacto.id})


@csrf_exempt
def calificacion_cliente_externa_view(request):
    """Servicio externo para calificar via post"""
    if request.method == 'POST':
        received_json_data = json.loads(request.body)
        # tener en cuenta que se espera json con estas claves
        data_esperada = ['pk_campana', 'id_cliente', 'id_calificacion', 'id_agente',
                         'user_api', 'password_api']
        for data in data_esperada:
            if data not in received_json_data.keys():
                return JsonResponse({'status': 'Error en falta {0}'.format(data)})

        try:
            usuario = UserApiCrm.objects.get(
                usuario=received_json_data['user_api'])
            received_password = received_json_data['password_api']
            if check_password(received_password, usuario.password):
                campana = Campana.objects.get(pk=received_json_data['pk_campana'])
                contacto = Contacto.objects.get(pk=received_json_data['id_cliente'])
                opcion_calificacion = OpcionCalificacion.objects.get(
                    pk=received_json_data['id_calificacion'])
                agente = AgenteProfile.objects.get(pk=received_json_data['id_agente'])
                try:
                    calificacion = CalificacionCliente.objects.get(
                        contacto=contacto, opcion_calificacion__campana=campana)
                    calificacion.opcion_calificacion = opcion_calificacion
                    calificacion.agente = agente
                    calificacion.save()
                except CalificacionCliente.DoesNotExist:
                    calificacion = CalificacionCliente.objects.create(
                        campana=campana, contacto=contacto, opcion_calificacion=opcion_calificacion,
                        agente=agente)
            else:
                return JsonResponse({'status': 'no coinciden usuario y/o password'})
        except UserApiCrm.DoesNotExist:
            return JsonResponse({'status': 'no existe este usuario {0}'.format(
                received_json_data['user_api'])})
        except Campana.DoesNotExist:
            return JsonResponse({'status': 'no existe esta campaña {0}'.format(
                received_json_data['pk_campana'])})
        except Contacto.DoesNotExist:
            return JsonResponse({'status': 'no existe este contacto {0}'.format(
                received_json_data['id_cliente'])})
        except CalificacionCliente.DoesNotExist:
            return JsonResponse({'status': 'no existe esta calificación {0}'.format(
                received_json_data['id_calificacion'])})
        except AgenteProfile.DoesNotExist:
            return JsonResponse({'status': 'no existe este perfil de agente {0}'.format(
                received_json_data['id_agente'])})
        return JsonResponse({'status': 'OK'})
    else:
        return JsonResponse({'status': 'este es un metodo post'})


######################################
# Respuesta de Formulario de Gestión #
######################################
class RespuestaFormularioDetailView(DetailView):
    """Vista muestra el formulario de gestion recientemente creado"""
    template_name = 'formulario/respuesta_formulario_detalle.html'
    model = RespuestaFormularioGestion

    def get_context_data(self, **kwargs):
        context = super(
            RespuestaFormularioDetailView, self).get_context_data(**kwargs)
        respuesta = RespuestaFormularioGestion.objects.get(pk=self.kwargs['pk'])
        contacto = respuesta.calificacion.contacto
        bd_contacto = contacto.bd_contacto
        nombres = bd_contacto.get_metadata().nombres_de_columnas_de_datos
        datos = json.loads(contacto.datos)
        mas_datos = []
        for nombre, dato in zip(nombres, datos):
            mas_datos.append((nombre, dato))

        context['contacto'] = contacto
        context['mas_datos'] = mas_datos
        context['metadata'] = json.loads(respuesta.metadata)

        return context


class RespuestaFormularioFormViewMixin(object):
    template_name = 'formulario/respuesta_formulario_create.html'
    model = RespuestaFormularioGestion
    form_class = RespuestaFormularioGestionForm

    def dispatch(self, *args, **kwargs):
        self.calificacion = self.get_object_calificacion()
        self.contacto = self.calificacion.contacto
        return super(RespuestaFormularioFormViewMixin, self).dispatch(*args, **kwargs)

    def get_contacto_form_kwargs(self):
        kwargs = {'instance': self.contacto,
                  'prefix': 'contacto_form',
                  'initial': {}}
        if self.request.method == "POST":
            kwargs['data'] = self.request.POST
        return kwargs

    def get_contacto_form(self):
        return FormularioNuevoContacto(**self.get_contacto_form_kwargs())

    def get_form_kwargs(self):
        kwargs = super(RespuestaFormularioFormViewMixin, self).get_form_kwargs()
        campana = self.calificacion.opcion_calificacion.campana
        campos = campana.formulario.campos.all()
        kwargs['campos'] = campos
        return kwargs

    def get(self, request, *args, **kwargs):
        contacto_form = self.get_contacto_form()
        form = self.get_form()
        return self.render_to_response(self.get_context_data(
            form=form, contacto_form=contacto_form))

    def form_valid(self, form, contacto_form):
        self.contacto = contacto_form.save(commit=False)
        self.contacto.datos = contacto_form.get_datos_json()
        self.contacto.save()

        self.object = form.save(commit=False)
        cleaned_data_respuesta = form.cleaned_data
        del cleaned_data_respuesta['calificacion']
        metadata = json.dumps(cleaned_data_respuesta)
        self.object.metadata = metadata
        self.object.calificacion = self.calificacion
        self.object.save()
        self.calificacion.agente = self.request.user.get_agente_profile()
        self.calificacion.save()
        message = _('Operación Exitosa!'
                    'Se llevó a cabo con éxito el llenado del formulario del'
                    ' cliente')
        messages.success(self.request, message)
        return HttpResponseRedirect(reverse('formulario_detalle',
                                            kwargs={"pk": self.object.pk}))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for validity.
        """
        contacto_form = self.get_contacto_form()
        form = self.get_form()

        if form.is_valid() and contacto_form.is_valid():
                return self.form_valid(form, contacto_form)
        else:
            return self.form_invalid(form, contacto_form)

    def form_invalid(self, form, contacto_form):

        message = '<strong>Operación Errónea!</strong> \
                  Error en el formulario revise bien los datos llenados.'

        messages.add_message(
            self.request,
            messages.WARNING,
            message,
        )
        return self.render_to_response(self.get_context_data(
            form=form, contacto_form=contacto_form))

    def get_success_url(self):
        reverse('view_blanco')


class RespuestaFormularioCreateFormView(RespuestaFormularioFormViewMixin, CreateView):
    """En esta vista se crea el formulario de gestion"""

    def dispatch(self, *args, **kwargs):
        self.object = None
        respuestas = RespuestaFormularioGestion.objects.filter(
            calificacion_id=self.kwargs['pk_calificacion'])
        if respuestas.count() > 0:
            return HttpResponseRedirect(reverse('formulario_venta_update',
                                                kwargs={"pk": respuestas[0].id}))
        return super(RespuestaFormularioCreateFormView, self).dispatch(*args, **kwargs)

    def get_object_calificacion(self):
        return CalificacionCliente.objects.get(id=self.kwargs['pk_calificacion'])

    def get_form_kwargs(self):
        kwargs = super(RespuestaFormularioCreateFormView, self).get_form_kwargs()
        kwargs['initial'].update({'calificacion': self.calificacion.id, })
        return kwargs


class RespuestaFormularioUpdateFormView(RespuestaFormularioFormViewMixin, UpdateView):
    """Vista para actualizar un formulario de gestion"""

    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()
        return super(RespuestaFormularioUpdateFormView, self).dispatch(*args, **kwargs)

    def get_object_calificacion(self):
        return self.object.calificacion

    def get_form_kwargs(self):
        kwargs = super(RespuestaFormularioUpdateFormView, self).get_form_kwargs()
        for clave, valor in json.loads(self.object.metadata).items():
            kwargs['initial'].update({clave: valor})
        return kwargs
