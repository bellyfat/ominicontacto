# -*- coding: utf-8 -*-

"""Vistas para la gestión de campañas entrantes"""

from __future__ import unicode_literals


from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from formtools.wizard.views import SessionWizardView

from ominicontacto_app.forms import (
    CampanaForm, QueueEntranteForm, OpcionCalificacionFormSet, ParametroExtraParaWebformFormSet
)
from ominicontacto_app.models import Campana, Queue, ArchivoDeAudio

from ominicontacto_app.services.creacion_queue import (ActivacionQueueService,
                                                       RestablecerDialplanError)
from ominicontacto_app.services.asterisk_service import AsteriskService

import logging as logging_

logger = logging_.getLogger(__name__)


class CampanaEntranteMixin(object):
    INICIAL = '0'
    COLA = '1'
    OPCIONES_CALIFICACION = '2'

    FORMS = [(INICIAL, CampanaForm),
             (COLA, QueueEntranteForm),
             (OPCIONES_CALIFICACION, OpcionCalificacionFormSet)]

    TEMPLATES = {INICIAL: "campana/nueva_edita_campana.html",
                 COLA: "campana/create_update_queue.html",
                 OPCIONES_CALIFICACION: "campana/opcion_calificacion.html"}

    form_list = FORMS

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]

    def get_form(self, step=None, data=None, files=None):
        if step is None:
            step = self.steps.current
        if step != self.COLA:
            return super(CampanaEntranteMixin, self).get_form(step, data, files)
        else:
            # se mantiene la mayor parte del código existente en el plug-in 'formtools
            # con la excepción de que se le pasa el argumento 'audio_choices' para instanciar
            # con éxito el formulario correspondiente
            audio_choices = ArchivoDeAudio.objects.all()
            form_class = self.form_list[step]
            kwargs = self.get_form_kwargs(step)
            kwargs.update({
                'data': data,
                'files': files,
                'prefix': self.get_form_prefix(step, form_class),
                'initial': self.get_form_initial(step),
            })
            if issubclass(form_class, (forms.ModelForm, forms.models.BaseInlineFormSet)):
                kwargs.setdefault('instance', self.get_form_instance(step))
            elif issubclass(form_class, forms.models.BaseModelFormSet):
                kwargs.setdefault('queryset', self.get_form_instance(step))
            return form_class(audio_choices, **kwargs)


class CampanaEntranteCreateView(CampanaEntranteMixin, SessionWizardView):
    """
    Esta vista crea una campaña entrante
    """

    def _save_queue(self, queue_form):
        queue_form.instance.eventmemberstatus = True
        queue_form.instance.eventwhencalled = True
        queue_form.instance.ringinuse = True
        queue_form.instance.setinterfacevar = True
        queue_form.instance.wrapuptime = 0
        queue_form.instance.queue_asterisk = Queue.objects.ultimo_queue_asterisk()
        audio_pk = queue_form.cleaned_data['audios']
        if audio_pk:
            audio = ArchivoDeAudio.objects.get(pk=int(audio_pk))
            queue_form.instance.announce = audio.audio_asterisk
        else:
            queue_form.instance.announce = None
        queue_form.instance.save()
        return queue_form.instance

    def _insert_queue_asterisk(self, queue):
        servicio_asterisk = AsteriskService()
        servicio_asterisk.insertar_cola_asterisk(queue)
        activacion_queue_service = ActivacionQueueService()
        try:
            activacion_queue_service.activar()
        except RestablecerDialplanError:
            raise

    def done(self, form_list, **kwargs):
        campana_form = form_list[int(self.INICIAL)]
        queue_form = form_list[int(self.COLA)]
        opciones_calificacion_formset = form_list[int(self.OPCIONES_CALIFICACION)]
        campana_form.instance.type = Campana.TYPE_ENTRANTE
        campana_form.instance.reported_by = self.request.user
        campana_form.instance.estado = Campana.ESTADO_ACTIVA
        campana_form.save()
        campana = campana_form.instance
        queue_form.instance.campana = campana
        queue = self._save_queue(queue_form)
        self._insert_queue_asterisk(queue)
        opciones_calificacion_formset.instance = campana
        opciones_calificacion_formset.save()
        return HttpResponseRedirect(reverse('campana_list'))

    def get_form_initial(self, step):
        initial_data = super(CampanaEntranteCreateView, self).get_form_initial(step)
        if step == self.COLA:
            step_cleaned_data = self.get_cleaned_data_for_step(self.INICIAL)
            name = step_cleaned_data['nombre']
            initial_data.update({'name': name})
        return initial_data


class CampanaEntranteUpdateView(CampanaEntranteMixin, SessionWizardView):
    """
    Esta vista modifica una campaña entrante
    """

    def done(self, form_list, *args, **kwargs):
        campana_form = form_list[int(self.INICIAL)]
        queue_form = form_list[int(self.COLA)]
        opciones_calificacion_formset = form_list[int(self.OPCIONES_CALIFICACION)]
        campana_form.instance.type = Campana.TYPE_ENTRANTE
        campana_form.instance.reported_by = self.request.user
        campana_form.instance.estado = Campana.ESTADO_ACTIVA
        campana_form.save()
        campana = campana_form.instance
        queue_form.instance.campana = campana
        # self._save_queue(queue_form)
        queue_form.save()
        opciones_calificacion_formset.instance = campana
        opciones_calificacion_formset.save()
        return HttpResponseRedirect(reverse('campana_list'))

    def get_form_instance(self, step):
        pk = self.kwargs.get('pk_campana', None)
        campana = get_object_or_404(Campana, pk=pk)
        if step == self.INICIAL:
            return campana
        if step == self.COLA:
            return campana.queue_campana

    def get_form_initial(self, step):
        if step == self.OPCIONES_CALIFICACION:
            campana = self.get_form_instance(self.INICIAL)
            opciones_calificacion = campana.opciones_calificacion.all()
            initial_data = [{'nombre': opcion_calificacion.nombre, 'tipo': opcion_calificacion.tipo}
                            for opcion_calificacion in opciones_calificacion]
            return initial_data
        return super(CampanaEntranteUpdateView, self).get_form_initial(step)
