/* Copyright (C) 2018 Freetech Solutions

 This file is part of OMniLeads

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see http://www.gnu.org/licenses/.

*/

$(function() {
       asociar_eventos_ocultar_campanas()
     });

     function asociar_eventos_ocultar_campanas(){
       $('.campana-mostrar-esconder').each(function(i, value){
         $(this).on('click', function() {
           var $show_node = $(this);
           var $show_state = $show_node.attr('data');
           var campana_pk = $(this).find('input').attr('value');
           $.post(Urls.campana_mostrar_ocultar(campana_pk))
            .done(function() {
              console.log('Done');
              if ($show_state == 'ocultar') {
                // eliminamos el nodo ocultando de esta manera la campaña
                $show_node.parents('tr').remove();
              }
              else {
                // cambiamos los atributos del nodo para mostrarlo como visible
                $show_node.attr('data', 'ocultar');
                var $show_node_span = $show_node.find('span');
                $show_node_span.attr('title', 'ocultar');
                $show_node_span.attr('class', 'glyphicon glyphicon-eye-close');
              }
            })
            .fail(function(data) {
              console.log('Error');
            });
         });
       });
     }

     function mostrar_campanas_preview_ocultas() {
       $.get(Urls.campana_preview_mostrar_ocultas(),
             function (data) {
               if (data.result == 'desconectado'){
                 //mostramos modal informativo de que el usuario está desconectado
                 $('#modal_desconectado').modal('show');
               }
               else {
                 // mostramos las campanas borradas
                 $('#t_body_borradas').html(data);
               }
             });
     };

     function mostrar_detalle_campana(pk_campana) {
       var $reporteModal = $('#reporteModal');
       var $modalContent = $reporteModal.find(".modal-body");
       $.get(Urls.campana_preview_detalle_express(pk_campana),
             function (data) {
               $modalContent.html(data);
               $reporteModal.modal('show');
             });
     };