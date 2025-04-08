from django.contrib import admin
from django.urls import path
from SafaRestaurantapp.views import (
    go_home_page, go_about_us, go_rol_page,
    go_cliente_view, go_camarero_view, go_cocinero_view, go_adminn_view,
    go_seguridad_admin, go_seguridad_camarero,
    cargar_listado_camareros, formulario_camarero, new_camarero, crear_editar, eliminar_camarero,
    generar_pdf,
    ver_pedidos, personalizar_hamburguesa, agregar_a_pedido, eliminar_pedido
)

urlpatterns = [
    # Página principal y estáticas
    path('home/', go_home_page, name='home_page'),
    path('aboutus/', go_about_us, name='about_us'),
    path('rol/', go_rol_page, name='rol_page'),

    # Roles
    path('cliente/', go_cliente_view, name='cliente'),
    path('camarero/', go_camarero_view, name='camarero'),
    path('cocinero/', go_cocinero_view, name='cocinero'),
    path('admin/', go_adminn_view, name='adminn'),

    # Seguridad
    path('segadmin/', go_seguridad_admin, name='seguridad_admin'),
    path('segcam/', go_seguridad_camarero, name='seguridad_camarero'),

    # Camareros
    path('camareros/', cargar_listado_camareros, name='admin'),
    path('form_camarero/', formulario_camarero, name='form_camarero'),
    path('admin/camarero/<int:id>', new_camarero, name='new_camarero'),
    path('editar_camarero/<int:id>', crear_editar, name='editar_camarero'),
    path('eliminar_camarero/<int:id>', eliminar_camarero, name='eliminar_camarero'),

    # PDF
    path('descargar_pdf/', generar_pdf, name='descargar_pdf'),

    # Pedidos
    path('pedidos/', ver_pedidos, name='ver_pedidos'),
    path('pedidos/<int:id>/personalizar/', personalizar_hamburguesa, name='personalizar_hamburguesa'),
    path('pedidos/<int:id>/agregar/', agregar_a_pedido, name='agregar_a_pedido'),
    path('eliminar_pedido/<int:id>/', eliminar_pedido, name='eliminar_pedido'),
]
