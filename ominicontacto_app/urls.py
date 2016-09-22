# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import url, patterns
from ominicontacto_app import (
    views, views_base_de_datos_contacto, views_contacto, views_campana_creacion,
    views_grabacion)
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^ajax/mensaje_recibidos/',
        views.mensajes_recibidos_view,
        name='ajax_mensaje_recibidos'),
    url(r'^$', views.index_view, name='index'),
    url(r'^accounts/login/$', views.login_view, name='login'),
    url(r'^user/nuevo/$',
        login_required(views.CustomerUserCreateView.as_view()),
        name='user_nuevo',
        ),
    url(r'^user/delete/(?P<pk>\d+)/$',
        login_required(views.UserDeleteView.as_view()),
        name='user_delete',
        ),
    url(r'^user/list/$', login_required(views.UserListView.as_view()),
        name='user_list',
        ),
    url(r'^user/update/(?P<pk>\d+)/$',
        login_required(views.CustomerUserUpdateView.as_view()),
        name='user_update',
        ),
    url(r'^user/agenteprofile/nuevo/(?P<pk_user>\d+)/$',
        login_required(views.AgenteProfileCreateView.as_view()),
        name='agenteprofile_nuevo',
        ),
    url(r'^modulo/nuevo/$',
        login_required(views.ModuloCreateView.as_view()), name='modulo_nuevo',
        ),
    url(r'^modulo/update/(?P<pk>\d+)/$',
        login_required(views.ModuloUpdateView.as_view()),
        name='modulo_update',
        ),
    url(r'^modulo/list/$',
        login_required(views.ModuloListView.as_view()), name='modulo_list',
        ),
    url(r'^modulo/delete/(?P<pk>\d+)/$',
        login_required(views.ModuloDeleteView.as_view()),
        name='modulo_delete',
        ),
    url(r'^agente/list/$',
        login_required(views.AgenteListView.as_view()), name='agente_list',
        ),
    url(r'^user/agenteprofile/update/(?P<pk_agenteprofile>\d+)/$',
        login_required(views.AgenteProfileUpdateView.as_view()),
        name='agenteprofile_update',
        ),
    url(r'^grupo/nuevo/$',
        login_required(views.GrupoCreateView.as_view()), name='grupo_nuevo',
        ),
    url(r'^grupo/update/(?P<pk>\d+)/$',
        login_required(views.GrupoUpdateView.as_view()),
        name='grupo_update',
        ),
    url(r'^grupo/list/$',
        login_required(views.GrupoListView.as_view()), name='grupo_list',
        ),
    url(r'^grupo/delete/(?P<pk>\d+)/$',
        login_required(views.GrupoDeleteView.as_view()),
        name='grupo_delete',
        ),
    url(r'^pausa/nuevo/$',
        login_required(views.PausaCreateView.as_view()),
        name='pausa_nuevo',
        ),
    url(r'^pausa/update/(?P<pk>\d+)/$',
        login_required(views.PausaUpdateView.as_view()),
        name='pausa_update',
        ),
    url(r'^pausa/list/$',
        login_required(views.PausaListView.as_view()),
        name='pausa_list',
        ),
    url(r'^pausa/delete/(?P<pk>\d+)/$',
        login_required(views.PausaDeleteView.as_view()),
        name='pausa_delete',
        ),
    url(r'^node/$', login_required(views.node_view), name='view_node'),
    url(r'^smsThread/$',
        login_required(views.mensajes_recibidos_enviado_remitente_view),
        name='view_sms_thread'),
    url(r'^sms/getAll/$',
        login_required(views.mensajes_recibidos_view),
        name='view_sms_get_all'),
    url(r'^blanco/$',
        login_required(views.blanco_view),
        name='view_blanco'),
    url(r'^grabacion/buscar/$',
        login_required(views.BusquedaGrabacionFormView.as_view()),
        name='grabacion_buscar',
        ),
    url(r'^agenda/nuevo/$',
        login_required(views.nuevo_evento_agenda_view),
        name='agenda_nuevo',
        ),
    url(r'^agenda/agente_list/$',
        login_required(views.AgenteEventosListView.as_view()),
        name='agenda_agente_list',
        ),
    # ==========================================================================
    # Base Datos Contacto
    # ==========================================================================
    url(r'^base_datos_contacto/(?P<pk_bd_contacto>\d+)/actualizar/$',
        login_required(views_base_de_datos_contacto.
                       BaseDatosContactoUpdateView.as_view()),
        name='update_base_datos_contacto'
        ),
    url(r'^base_datos_contacto/nueva/$',
        login_required(views_base_de_datos_contacto.
                       BaseDatosContactoCreateView.as_view()),
        name='nueva_base_datos_contacto'
        ),
    url(r'^base_datos_contacto/(?P<pk>\d+)/validacion/$',
        login_required(views_base_de_datos_contacto.
                       DefineBaseDatosContactoView.as_view()),
        name='define_base_datos_contacto',
        ),
    url(r'^base_datos_contacto/$',
        login_required(views_base_de_datos_contacto.
                       BaseDatosContactoListView.as_view()),
        name='lista_base_datos_contacto',
        ),
    url(r'^base_datos_contacto/(?P<bd_contacto>\d+)/agregar/$',
        login_required(views_contacto.ContactoBDContactoCreateView.as_view()),
        name='agregar_contacto',
        ),
    url(r'^contacto/nuevo/$',
        login_required(views_contacto.ContactoCreateView.as_view()),
        name='contacto_nuevo',
        ),
    url(r'^contacto/list/(?P<pagina>\d+)/$',
        login_required(views_contacto.ContactoListView.as_view()),
        name='contacto_list',
        ),
    url(r'^contacto/(?P<id_cliente>\d+)/update/$',
        login_required(views_contacto.ContactoUpdateView.as_view()),
        name='contacto_update',
        ),
    url(r'^contacto/(?P<telefono>[\w\-]+)/list/$',
        login_required(views_contacto.ContactoTelefonoListView.as_view()),
        name='contacto_list_telefono',
        ),
    url(r'^contacto/buscar/$',
        login_required(views_contacto.BusquedaContactoFormView.as_view()),
        name='contacto_buscar',
        ),
    url(r'^contacto/(?P<id_cliente>\d+)/id_cliente/$',
        login_required(views_contacto.ContactoIdClienteListView.as_view()),
        name='contacto_list_id_cliente',
        ),
    url(r'^base_datos_contacto/(?P<bd_contacto>\d+)/list_contacto/$',
        login_required(views_contacto.ContactoBDContactoListView.as_view()),
        name='contacto_list_bd_contacto',
        ),
    url(r'^base_datos_contacto/(?P<pk_contacto>\d+)/update/$',
        login_required(views_contacto.ContactoBDContactoUpdateView.as_view()),
        name='actualizar_contacto',
        ),
    url(r'^base_datos_contacto/(?P<pk_contacto>\d+)/eliminar/$',
        login_required(views_contacto.ContactoBDContactoDeleteView.as_view()),
        name='eliminar_contacto',
        ),
    url(r'^base_datos_contacto/(?P<bd_contacto>\d+)/exporta/$',
        login_required(
            views_base_de_datos_contacto.ExportaBDContactosView.as_view()),
        name='exporta_base_datos_contactos',
        ),
    # ==========================================================================
    # Campana
    # ==========================================================================
    url(r'^campana/nuevo/$',
        login_required(views_campana_creacion.CampanaCreateView.as_view()),
        name='campana_nuevo',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/update/$',
        login_required(views_campana_creacion.CampanaUpdateView.as_view()),
        name='campana_update',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/cola/$',
        login_required(views_campana_creacion.QueueCreateView.as_view()),
        name='queue_nuevo',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/queue_member/$',
        login_required(views_campana_creacion.QueueMemberCreateView.as_view()),
        name='queue_member',
        ),
    url(r'queue/list/$',
        login_required(views_campana_creacion.QueueListView.as_view()),
        name='queue_list',
        ),
    url(r'^queue/elimina/(?P<pk_queue>[\w\-]+)/$',
        login_required(views_campana_creacion.QueueDeleteView.as_view()),
        name='queue_elimina',
        ),
    url(r'^campana/update/(?P<pk_campana>\d+)/cola/$',
        login_required(views_campana_creacion.QueueUpdateView.as_view()),
        name='queue_update',
        ),
    url(
        r'^queue_member/(?P<pk_queuemember>\d+)/elimina/(?P<pk_campana>\d+)/$',
        login_required(views_campana_creacion.queue_member_delete_view),
        name='queuemember_elimina',
        ),
    url(r'campana/list/$',
        login_required(views_campana_creacion.CampanaListView.as_view()),
        name='campana_list',
        ),
    url(r'^campana/elimina/(?P<pk_campana>\d+)/$',
        login_required(views_campana_creacion.CampanaDeleteView.as_view()),
        name='campana_elimina',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/formulario/(?P<id_cliente>\d+)/$',
        login_required(
            views_campana_creacion.FormularioDemoFormUpdateView.as_view()),
        name='formulario_update',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/formulario_nuevo/$',
        login_required(
            views_campana_creacion.FormularioDemoFormCreateView.as_view()),
        name='formulario_nuevo',
        ),
    url(r'^formulario/(?P<pk_campana>\d+)/update/(?P<id_cliente>\d+)/$',
        login_required(
            views_campana_creacion.ContactoFormularioUpdateView.as_view()),
        name='formulario_update_contacto',
        ),
    url(r'^formulario/(?P<pk_campana>\d+)/buscar/$',
        login_required(
            views_campana_creacion.BusquedaFormularioFormView.as_view()),
        name='formulario_buscar',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/exporta/$',
        login_required(
            views_campana_creacion.ExportaReporteCampanaView.as_view()),
        name='exporta_campana_reporte',
        ),
    url(r'^campana/(?P<pk_campana>\d+)/reporte/$',
        login_required(
            views_campana_creacion.CampanaReporteListView.as_view()),
        name='reporte_campana',
        ),
    # ==========================================================================
    # Reportes
    # ==========================================================================
    url(r'^reporte/llamadas/hoy/$',
        login_required(views_grabacion.GrabacionReporteListView.as_view()),
        name='reporte_llamadas_hoy',
        ),
    url(r'^reporte/llamadas/semana/$',
        login_required(views_grabacion.GrabacionReporteSemanaListView.as_view()),
        name='reporte_llamadas_semana',
        ),
    url(r'^reporte/llamadas/mes/$',
        login_required(
            views_grabacion.GrabacionReporteMesListView.as_view()),
        name='reporte_llamadas_mes',
        ),
]

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT}))
