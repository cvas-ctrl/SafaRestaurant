from django.contrib import admin
from django.urls import path
from SafaRestaurantapp.views import (
    go_home_page, go_about_us, go_rol_page,
    go_cliente_view, go_camarero_view, go_cocinero_view, go_adminn_view,
    gestion_acceso, iniciar_pedido,
    cargar_listado_camareros, formulario_camarero, new_camarero, crear_editar, eliminar_camarero,
    generar_pdf, cargar_listado_cocineros,
    ver_pedidos, personalizar_hamburguesa, agregar_a_pedido, eliminar_pedido, formulario_cocinero,
    crear_editar_cocinero, eliminar_cocinero, go_register, seleccionar_cliente, asignar_cliente, liberar_mesa,
    finalizar_pedido, ver_cuentas, eliminar_pedido_finalizado, go_login, go_logout, pedidos_pendientes_cocina,
    marcar_pedido_preparado, ir_carta, personalizar_carta, add_carrito, ver_carrito, comprar, confirmacion,
    eliminar_del_carrito, nueva_mesa, editar_mesa, eliminar_mesa, nueva_hamburguesa, editar_hamburguesa,
    eliminar_hamburguesa, perfil_usuario, sumar_carrito, restar_carrito, pedidos_admin, eliminar_pedido_admin,
    pedidos_cliente, editar_nombre_usuario, analisis_mensual, editar_pedido, generar_reporte_mensual, ir_reserva,
    nueva_reserva, editar_reserva, eliminar_reserva

)

urlpatterns = [

    # Página principal y estáticas
    path('home/', go_home_page, name='home_page'),
    path('aboutus/', go_about_us, name='about_us'),
    path('rol/', go_rol_page, name='rol_page'),
    path('register/', go_register, name='register_page'),
    path('login/', go_login, name='login_page'),
    path('editar/login/', editar_nombre_usuario, name='editar_nombre_usuario'),
    path('logout/', go_logout, name='logout'),
    path('perfil/', perfil_usuario, name='perfil'),

    # Roles
    path('cliente/', go_cliente_view, name='cliente'),
    path('camarero/', go_camarero_view, name='camarero'),
    path('cocina/', go_cocinero_view, name='cocinero'),
    path('admin/', go_adminn_view, name='adminn'),

    # Seguridad
    path('seguridad/', gestion_acceso, name='gestion_acceso'),

    # Camareros
    path('camareros/', cargar_listado_camareros, name='admin'),
    path('form_camarero/', formulario_camarero, name='form_camarero'),
    path('admin/camarero/<int:id>', new_camarero, name='new_camarero'),
    path('editar_camarero/<int:id>', crear_editar, name='editar_camarero'),
    path('eliminar_camarero/<int:id>', eliminar_camarero, name='eliminar_camarero'),

    # PDF
    path('descargar_pdf/', generar_pdf, name='descargar_pdf'),

    # Pedidos
    path('iniciar_pedido/<int:mesa_id>/', iniciar_pedido, name='iniciar_pedido'),

    path('pedidos/', ver_pedidos, name='ver_pedidos'),
    path('pedidos/<int:id>/personalizar/', personalizar_hamburguesa, name='personalizar_hamburguesa'),
    path('pedidos/<int:id>/agregar/', agregar_a_pedido, name='agregar_a_pedido'),
    path('eliminar_pedido/<int:id>/', eliminar_pedido, name='eliminar_pedido'),

    # CUENTAS
    path('editar_pedido/<int:id>/', editar_pedido, name='editar_pedido'),

    path('pedidos/finalizar/', finalizar_pedido, name='finalizar_pedido'),
    path('cuentas/', ver_cuentas, name='ver_cuentas'),
    path('cuentas/eliminar/<int:id>/', eliminar_pedido_finalizado, name='eliminar_pedido_finalizado'),


    #COCINERO
    path('cocineros/', cargar_listado_cocineros, name='cocineros'),
    path('cocinero/', crear_editar_cocinero, name='crear_cocinero'),
    path('cocinero/<int:id>/', crear_editar_cocinero, name='editar_cocinero'),
    path('eliminar_cocinero/<int:id>', eliminar_cocinero, name='eliminar_cocinero'),
    path('cocina/pedidos/', pedidos_pendientes_cocina, name='pedidos_pendientes_cocina'),
    path('cocina/marcar/<int:pedido_id>/', marcar_pedido_preparado, name='marcar_pedido_preparado'),


    # GESTION DE MESAS Y CLIENTES
    path('mesa/<int:mesa_id>/seleccionar-cliente/', seleccionar_cliente, name='seleccionar_cliente'),
    path('mesa/<int:mesa_id>/asignar-cliente/', asignar_cliente, name='asignar_cliente'),
    path('mesa/<int:mesa_id>/liberar/', liberar_mesa, name='liberar_mesa'),

    # CLIENTE
    path('reserva/', ir_reserva, name='ir_reserva'),
    path('reserva/nueva/', nueva_reserva, name='nueva_reserva'),
    path('reserva/editar/<int:id>/', editar_reserva, name='editar_reserva'),
    path('reserva/eliminar/<int:id>/', eliminar_reserva, name='eliminar_reserva'),
    path('carta/', ir_carta, name='ir_carta'),
    path('carta/<int:id>/personalizar/', personalizar_carta, name='personalizar_carta'),
    path('carrito/add/<int:id>/', add_carrito, name='add_carrito'),
    path('eliminar_del_carrito/<int:id>/', eliminar_del_carrito, name='eliminar_del_carrito'),
    path('ver_carrito/', ver_carrito, name='ver_carrito'),
    path('carrito/sumar/<int:id>/', sumar_carrito, name='sumar_carrito'),
    path('carrito/restar/<int:id>/', restar_carrito, name='restar_carrito'),
    path('completar_compra/', comprar, name='comprar'),
    path('confirmacion/', confirmacion, name='confirmacion'),

    # ADMIN
    path('mesa/nueva/', nueva_mesa, name='nueva_mesa'),
    path('mesa/editar/<int:id>/', editar_mesa, name='editar_mesa'),
    path('mesa/eliminar/<int:id>/', eliminar_mesa, name='eliminar_mesa'),
    path('hamburguesa/nueva/', nueva_hamburguesa, name='nueva_hamburguesa'),
    path('hamburguesa/editar/<int:id>/', editar_hamburguesa, name='editar_hamburguesa'),
    path('hamburguesa/eliminar/<int:id>/', eliminar_hamburguesa, name='eliminar_hamburguesa'),
    path('pedidos/admin/', pedidos_admin, name='pedidos_admin'),
    path('admin/pedidos/eliminar/<int:pedido_id>/', eliminar_pedido_admin, name='eliminar_pedido_admin'),
    path('pedidos/cliente/', pedidos_cliente, name='pedidos_cliente'),
    path('admin/analisis_mensual/',analisis_mensual, name='analisis_mensual'),

    path('generar_reporte/', generar_reporte_mensual, name='generar_reporte'),

]


