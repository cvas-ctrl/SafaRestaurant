from datetime import time, datetime, timezone
from decimal import Decimal

from PIL.ImImagePlugin import number
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.db.models import PositiveIntegerField
from django.forms import IntegerField
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from SafaRestaurantapp.forms import *
from SafaRestaurantapp.models import Camarero, Hamburguesa, Ingrediente, Cocinero, TareaCocina, TipoCocinero, \
    DetallePedido, Pedido, IngredienteDetalle, Mesa, Cliente, Cuenta, EstadoProducto, EstadoPedido, EstadoCuenta, \
    ReporteMensualVentas, Reserva


# ============================ PÁGINAS ESTÁTICAS ============================

def go_home_page(request):
    return render(request, 'home.html')

def go_about_us(request):
    return render(request, 'about_us.html')
@login_required
def go_rol_page(request):
    return render(request, 'rol.html')

Usuario = get_user_model()

def go_register(request):

    form = RegistroForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            usuario_nuevo = form.save()
            return redirect('home_page')

    return render(request, "register.html", {'form': form})

def go_login(request):
   form = LoginForm()
   if request.method == 'POST':
       form = LoginForm(request, data=request.POST)
       if form.is_valid():
           email = form.cleaned_data.get('username')
           password = form.cleaned_data.get('password')
           usuario = authenticate(request, email=email, password=password)
           if usuario is not None:
               login(request, usuario)
               return redirect('home_page')
       return render(request, "login.html", {'form': form})
   else:
       return render(request, "login.html", {'form': form})

@login_required
def editar_nombre_usuario(request):
    if request.method == 'POST':
        nuevo_nombre = request.POST.get('nombre')
        if nuevo_nombre:
            usuario = request.user
            usuario.nombre = nuevo_nombre
            usuario.save()
            messages.success(request, 'Te has cambiado el nombre con exito')
            return redirect('editar_nombre_usuario')
        else:
            return render(request, 'editar_nombre_usuario.html', {'error': 'El nombre de usuario no puede estar vacío.'})
    else:
        return render(request, 'editar_nombre_usuario.html')


def go_logout(request):
    logout(request)
    return redirect('login_page')

# ============================ SEGURIDAD DE GESTIONES ============================
@login_required
def gestion_acceso(request):
   rol_seleccionado = request.GET.get('rol')


   if request.method == 'POST':
       form = AccesoEmpleadoForm(request.POST)
       if form.is_valid():
           rol = form.cleaned_data['rol']


           if request.user.rol != rol:
               form.add_error(None, "No puedes acceder con un rol diferente al tuyo.")
           else:
               if rol == 'admin':
                   return redirect('adminn')
               elif rol == 'cocinero':
                   return redirect('cocinero')
               elif rol == 'camarero':
                   return redirect('camarero')
   else:
       form = AccesoEmpleadoForm(initial={'rol': rol_seleccionado})


   return render(request, "gestion_acceso.html", {'form': form})


# ============================ BLOQUE DE URLS ============================

def es_admin_o_cliente(user):
   if not user.is_authenticated or user.rol not in ['admin', 'cliente']:
       raise PermissionDenied
   return True

def es_admin_o_camarero(user):
   if not user.is_authenticated or user.rol not in ['admin', 'camarero']:
       raise PermissionDenied
   return True

def es_admin(user):
    if not user.is_authenticated or not user.rol == 'admin':
        raise PermissionDenied
    return True

def es_cocinero(user):
    if not user.is_authenticated or not user.rol == 'cocinero':
        raise PermissionDenied
    return True

def es_camarero(user):
    if not user.is_authenticated or not user.rol == 'camarero':
        raise PermissionDenied
    return True

def es_cliente(user):
    if not user.is_authenticated or not user.rol == 'cliente':
        raise PermissionDenied
    return True

# ============================ VISTAS POR ROL ============================

def go_cliente_view(request):
    return render(request, 'cliente.html')

@user_passes_test(es_admin_o_camarero)
def go_camarero_view(request):
    if not Mesa.objects.exists():
        for i in range(1, 6):
            Mesa.objects.create(numero=i)

    mesas = Mesa.objects.select_related('cliente', 'camarero').all()

    for mesa in mesas:
        pedido_activo = mesa.pedidos.filter(estado__in=[
            EstadoPedido.EN_COCINA,
            EstadoPedido.EN_PROCESO,
            EstadoPedido.FINALIZADO
        ])

        mesa.pedido_activo = pedido_activo

    return render(request, 'camarero.html', {
        'mesas': mesas,
        'clientes': Cliente.objects.all(),
        'camareros': Camarero.objects.all()
    })

@user_passes_test(es_cocinero)
def go_cocinero_view(request):
    pedidos = Pedido.objects.filter(
        estado=EstadoPedido.EN_COCINA,
        detalles__estado='EN_ESPERA'
    ).distinct().select_related('mesa').prefetch_related('detalles__hamburguesa')

    return render(request, 'cocinero.html', {
        'pedidos': pedidos
    })
@user_passes_test(es_admin)
def go_adminn_view(request):
    return render(request, 'adminn.html')

# ============================ CAMAREROS(admin) ============================
@user_passes_test(es_admin)
def formulario_camarero(request):
    return render(request, 'formulario_camarero.html')

@user_passes_test(es_admin)
def new_camarero(request, id):
    camarero = Camarero.objects.filter(id=id)

    if len(camarero) == 0:
        camarero_nuevo = Camarero()
    else:
        camarero_nuevo = camarero[0]

    if request.method == 'POST':
        camarero_nuevo.nombre = request.POST['nombre']
        camarero_nuevo.apellidos = request.POST['apellidos']
        camarero_nuevo.dni = request.POST['dni']
        camarero_nuevo.email = request.POST['email']
        camarero_nuevo.fecha_nacimiento = request.POST['fecha']

        camarero_nuevo.save()

        return redirect('admin')
    else:
        return render(request, 'formulario_camarero.html', {'camarero': camarero_nuevo})

@user_passes_test(es_admin)
def cargar_listado_camareros(request):
    lista_camareros = Camarero.objects.all()
    return render(request, 'admin.html', {'camareros': lista_camareros})

@user_passes_test(es_admin)
def crear_editar(request, id):
    camarero = get_object_or_404(Camarero, id=id) if id != 0 else None

    if request.method == 'POST':
        form = CamareroForm(request.POST, instance=camarero)
        if form.is_valid():
            form.save()
            return redirect('admin')
        return render(request, 'formulario_camarero.html')
    else:
        form = CamareroForm(instance=camarero)
        return render(request, 'formulario_camarero.html', {'form': form})

def eliminar_camarero(request, id):
    camarero = get_object_or_404(Camarero, id=id)
    camarero.delete()
    return redirect('admin')

# ============================ PDF ============================
def generar_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte.pdf"'

    p = canvas.Canvas(response)
    p.drawString(100, 750, "Hola, este es un PDF generado en Django")
    p.showPage()
    p.save()
    return response

# ============================ PEDIDOS (LO TOMA EL CAMARERO) ============================

def iniciar_pedido(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)

    pedido = Pedido.objects.filter(
        mesa=mesa,
        estado=EstadoPedido.EN_PROCESO
    ).first()

    if not pedido:
        pedido = Pedido.objects.create(
            mesa=mesa,
            estado=EstadoPedido.EN_PROCESO
        )

    request.session['mesa_id'] = mesa_id
    request.session['pedido_id'] = pedido.id

    return redirect('ver_pedidos')


@user_passes_test(es_camarero)
def ver_pedidos(request):
    pedido_id = request.session.get('pedido_id')
    pedido = None

    if pedido_id:
        try:
            pedido = Pedido.objects.prefetch_related(
                'detalles__hamburguesa',
                'detalles__ingredientedetalle_set__ingrediente'
            ).get(id=pedido_id)
        except Pedido.DoesNotExist:
            del request.session['pedido_id']

    hamburguesas = Hamburguesa.objects.all()
    return render(request, 'pedidos.html', {
        'hamburguesas': hamburguesas,
        'pedido': pedido
    })

@user_passes_test(es_camarero)
def personalizar_hamburguesa(request, id):
    hamburguesa = get_object_or_404(Hamburguesa, id=id)
    ingredientes = Ingrediente.objects.all()
    return render(request, 'personalizar.html', {
        'hamburguesa': hamburguesa,
        'todos_ingredientes': ingredientes
    })

def agregar_a_pedido(request, id):
    if request.method == 'POST':
        hamburguesa = get_object_or_404(Hamburguesa, id=id)

        pedido_id = request.session.get('pedido_id')
        if pedido_id:
            pedido = get_object_or_404(Pedido, id=pedido_id)
        else:
            mesa_id = request.session.get('mesa_id')
            mesa = Mesa.objects.get(id=mesa_id) if mesa_id else None
            pedido = Pedido.objects.create(mesa=mesa)
            request.session['pedido_id'] = pedido.id

        detalle = DetallePedido.objects.create(
            pedido=pedido,
            hamburguesa=hamburguesa,
            precio=hamburguesa.precio,
            cantidad=1
        )

        for key, value in request.POST.items():
            if key.startswith('ingredientes_') and int(value) > 0:
                ingrediente_id = int(key.split('_')[1])
                ingrediente = get_object_or_404(Ingrediente, id=ingrediente_id)
                IngredienteDetalle.objects.create(
                    detalle=detalle,
                    ingrediente=ingrediente,
                    cantidad=int(value)
                )

        return redirect('ver_pedidos')


def eliminar_pedido(request, id):
    pedido_id = request.session.get('pedido_id')
    if pedido_id:
        pedido = Pedido.objects.get(id=pedido_id)
        detalles = list(pedido.detalles.all())
        if 0 <= id < len(detalles):
            detalles[id].delete()

            if not pedido.detalles.exists():
                pedido.delete()
                del request.session['pedido_id']

    return redirect('ver_pedidos')


# ============================ COCINEROS(ADMIN) ============================
@user_passes_test(es_admin)
def cargar_listado_cocineros(request):
    cocineros = Cocinero.objects.prefetch_related('tareas').all()

    return render(request, 'cocineros.html', {
        'cocineros': cocineros
    })

@user_passes_test(es_admin)
def formulario_cocinero(request):
    return render(request, 'formulario_cocinero.html')

@user_passes_test(es_admin)
def crear_editar_cocinero(request, id=None):
    if id:
        cocinero = Cocinero.objects.get(id=id)
        tarea = TareaCocina.objects.filter(cocinero=cocinero).first()
    else:
        cocinero = Cocinero()
        tarea = None

    if request.method == 'POST':
        cocinero.nombre = request.POST['nombre']
        cocinero.apellidos = request.POST['apellidos']
        cocinero.dni = request.POST['dni']
        cocinero.email = request.POST['email']
        cocinero.fecha_nacimiento = request.POST['fecha']
        cocinero.save()

        if not tarea:
            tarea = TareaCocina(cocinero=cocinero)

        tarea.tipo = request.POST['tipo']
        tarea.save()

        return redirect('cocineros')
    else:
        elecciones = TipoCocinero.choices
        return render(request, 'formulario_cocinero.html', {
            'elecciones': elecciones,
            'cocinero': cocinero,
            'tipo_actual': tarea.tipo if tarea else None
        })

def eliminar_cocinero(request, id):
    cocinero = get_object_or_404(Cocinero, id=id)
    cocinero.tareas.all().delete()
    cocinero.delete()
    return redirect('cocineros')

# ============================ GESTION MESAS CLIENTES(DENTRO DE ADMIN) ===========================
# def gestion_mesas(request):

# ============================ GESTION MESAS CLIENTES ===========================


@user_passes_test(es_camarero)
def seleccionar_cliente(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    clientes = Cliente.objects.all()
    return render(request, 'seleccionar_cliente.html', {
        'mesa': mesa,
        'clientes': clientes
    })

@user_passes_test(es_camarero)
def asignar_cliente(request, mesa_id, cliente_id=None):
    mesa = get_object_or_404(Mesa, id=mesa_id)

    if cliente_id or request.method == 'POST':
        cliente_id = cliente_id or request.POST.get('cliente_id')
        cliente = get_object_or_404(Cliente, id=cliente_id)

        mesa.cliente = cliente
        mesa.estado = 'OCUPADA'
        mesa.save()
        return redirect('camarero')

    clientes = Cliente.objects.all()
    return render(request, 'seleccionar_cliente.html', {
        'mesa': mesa,
        'clientes': clientes
    })


def liberar_mesa(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    mesa.estado = 'LIBRE'
    mesa.cliente = None
    mesa.save()
    return redirect('camarero')

# ============================ CUENTAS ============================

@user_passes_test(es_camarero)
def editar_pedido(request, id):
    pedido = get_object_or_404(Pedido, id=id)

    if pedido.estado != EstadoPedido.EN_COCINA:
        return redirect('ver_cuentas')

    request.session['pedido_id'] = pedido.id
    request.session['mesa_id'] = pedido.mesa.id if pedido.mesa else None

    return redirect('ver_pedidos')

def finalizar_pedido(request):
    pedido_id = request.session.get('pedido_id')
    if pedido_id:
        pedido = get_object_or_404(Pedido, id=pedido_id)

        pedido.estado = EstadoPedido.EN_COCINA
        pedido.save()

        for detalle in pedido.detalles.all():
            detalle.estado = 'EN_ESPERA'
            detalle.save()

        if not hasattr(pedido, 'cuenta'):
            Cuenta.objects.create(pedido=pedido, precio_total=pedido.precio_total)

        if pedido.mesa:
            mesa = pedido.mesa
            mesa.estado = 'ESPERANDO'
            mesa.save()

        del request.session['pedido_id']

    return redirect('camarero')

def eliminar_pedido_finalizado(request, id):
    pedido = get_object_or_404(Pedido, id=id)
    pedido.delete()
    return redirect('ver_cuentas')

@user_passes_test(es_camarero)
def ver_cuentas(request):
    pedidos = Pedido.objects.filter(estado__in=[EstadoPedido.EN_COCINA, EstadoPedido.FINALIZADO])
    for pedido in pedidos:
        if not hasattr(pedido, 'cuenta'):
            Cuenta.objects.create(pedido=pedido, precio_total=pedido.precio_total)
    return render(request, 'cuentas.html', {
        'pedidos': pedidos
    })

# ============================ COCINA ============================

def pedidos_pendientes_cocina(request):
    pedidos = Pedido.objects.filter(
        estado=EstadoPedido.EN_COCINA,
        detalles__estado='EN_ESPERA'
    ).distinct().prefetch_related('detalles__hamburguesa', 'mesa')

    return render(request, 'cocinero.html', {'pedidos': pedidos})



def marcar_pedido_preparado(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.method == 'POST':
        pedido.detalles.filter(estado='EN_ESPERA').update(estado='PREPARADO')
        pedido.estado = EstadoPedido.FINALIZADO
        pedido.save()

        if pedido.mesa:
            pedido.mesa.estado = 'OCUPADA'
            pedido.mesa.save()

    return redirect('pedidos_pendientes_cocina')

# ============================ ERRORES ============================

def error_403(request, exception=None):
    return render(request, '403.html', status=403)

# ============================ CLIENTE ============================

@user_passes_test(es_cliente)
def ir_reserva(request):
    listado_reservas = Reserva.objects.filter(usuario=request.user)
    return render(request, 'reservas.html', {'reservas': listado_reservas })

# @user_passes_test(es_cliente)
# def nueva_reserva(request):
#    if request.method == 'POST':
#        form = ReservaForm(request.POST)
#        nueva_reserva = Reserva.objects.create(
#            numero_personas=IntegerField(),
#            hora_reserva=time(),
#            fecha_reserva=datetime.now(),
#            usuario=request.user
#        )
#        if form.is_valid():
#            form.save()
#            nueva_reserva.save()
#            return redirect('ir_reserva')
#    else:
#        form = ReservaForm()
#
#    return render(request, 'form_reserva.html', {'form': form})


@user_passes_test(es_cliente)
@login_required
def nueva_reserva(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.usuario = request.user
            reserva.save()
            messages.success(request, '¡Reserva creada con éxito!')
            return redirect('ir_reserva')
        else:
            messages.error(request, 'Hubo un error al crear la reserva. Por favor, revisa los datos.')
    else:
        form = ReservaForm()

    return render(request, 'form_reserva.html', {'form': form})

# @user_passes_test(es_cliente)
# def editar_reserva(request, id):
#    reserva = get_object_or_404(Reserva, id=id)
#    if request.method == 'POST':
#        form = ReservaForm(request.POST, instance=reserva)
#        if form.is_valid():
#            form.save()
#            return redirect('ir_reserva')
#    else:
#        form = ReservaForm(instance=reserva)
#
#    return render(request, 'form_reserva.html', {'form': form})

@user_passes_test(es_cliente)
@login_required
def editar_reserva(request, id):
    reserva = get_object_or_404(Reserva, id=id, usuario=request.user)
    if request.method == 'POST':
        form = ReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reserva actualizada con éxito.')
            return redirect('ir_reserva')
    else:
        form = ReservaForm(instance=reserva)

    return render(request, 'form_reserva.html', {'form': form})

@user_passes_test(es_cliente)
def eliminar_reserva(request, id):
   reserva = get_object_or_404(Reserva, id=id)
   reserva.delete()
   return redirect('ir_reserva')


# @user_passes_test(es_cliente)
# @login_required
# def eliminar_reserva(request, id):
#     reserva = get_object_or_404(Reserva, id=id, usuario=request.user)
#     if request.method == 'POST':
#         reserva.estado = 'CANCELADA'
#         reserva.save()
#         messages.info(request, 'Tu reserva ha sido cancelada correctamente.')
#         return redirect('ir_reserva')
#     return render(request, 'reservas.html', {'reserva': reserva})

@user_passes_test(es_cliente)
def ir_blog(request):
    listado_articulos = Articulo.objects.filter(autor=request.user)
    return render(request, 'articulos.html', {'articulos': listado_articulos })

@user_passes_test(es_cliente)
@login_required
def nuevo_articulo(request):
    if request.method == 'POST':
        form = ArticuloForm(request.POST)
        if form.is_valid():
            articulo = form.save(commit=False)
            articulo.autor = request.user
            articulo.save()
            messages.success(request, '¡Articulo creado con éxito!')
            return redirect('ir_blog')
        else:
            messages.error(request, 'Hubo un error al crear el articulo. Por favor, revisa los datos.')
    else:
        form = ArticuloForm()

    return render(request, 'form_articulo.html', {'form': form})

@user_passes_test(es_cliente)
@login_required
def editar_articulo(request, id):
    articulo = get_object_or_404(Articulo, id=id, autor=request.user)
    if request.method == 'POST':
        form = ArticuloForm(request.POST, instance=articulo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Articulo actualizado con éxito.')
            return redirect('ir_blog')
    else:
        form = ArticuloForm(instance=articulo)

    return render(request, 'form_articulo.html', {'form': form})

@user_passes_test(es_cliente)
def eliminar_articulo(request, id):
   articulo = get_object_or_404(Articulo, id=id)
   articulo.delete()
   return redirect('ir_blog')

@user_passes_test(es_admin_o_cliente)
def ir_carta(request):
    listado_hamburguesas = Hamburguesa.objects.all()
    return render(request, 'carta.html', {'hamburguesas': listado_hamburguesas})

@user_passes_test(es_cliente)
def personalizar_carta(request, id):
    hamburguesa = get_object_or_404(Hamburguesa, id=id)
    ingredientes = Ingrediente.objects.all()
    return render(request, 'personalizar_carta.html', {
        'hamburguesa': hamburguesa,
        'todos_ingredientes': ingredientes
    })

def restar_carrito(request, id):
    carrito = request.session.get('carrito', {})
    producto_id = str(id)

    if producto_id in carrito:
        if carrito[producto_id] > 1:
            carrito[producto_id] -= 1
        else:
            del carrito[producto_id]

    request.session['carrito'] = carrito
    return redirect('ver_carrito')

def sumar_carrito(request, id):
    carrito = request.session.get('carrito', {})
    producto_id = str(id)

    carrito[producto_id] = carrito.get(producto_id, 0) + 1

    request.session['carrito'] = carrito
    return redirect('ver_carrito')

def add_carrito(request, id):
    carrito = request.session.get('carrito', {})
    producto_en_carrito = carrito.get(str(id),0)

    if producto_en_carrito == 0:

        carrito[str(id)] = 1

    else:

        carrito[str(id)] += 1

    request.session['carrito'] = carrito
    messages.success(request, "Producto añadido correctamente al carrito.")
    return redirect('ir_carta')


def eliminar_del_carrito(request, id):
    if request.method == 'POST':
        carrito = request.session.get('carrito', {})

        hamburguesa_id = str(id)

        if hamburguesa_id in carrito:
            del carrito[hamburguesa_id]
            request.session['carrito'] = carrito

            if not carrito:
                del request.session['carrito']

    return redirect('ver_carrito')

@user_passes_test(es_cliente)
def ver_carrito(request):
    carrito = {}
    total = Decimal('0.0')

    carrito_session = request.session.get('carrito', {})

    for k, v in carrito_session.items():
        hamburguesa = Hamburguesa.objects.get(id=k)
        carrito[hamburguesa] = v
        total += Decimal(str(hamburguesa.precio)) * Decimal(v)

    return render(request, 'carrito.html', {
        'carrito': carrito,
        'total': float(total)
    })

@user_passes_test(es_cliente)
@login_required
def comprar(request):
   if not request.user.is_authenticated:
       return redirect('login')

   nuevo_pedido = Pedido.objects.create(
       codigo=f'PED-{datetime.now().strftime("%H%M%S")}',
       fecha=datetime.now(),
       estado=EstadoPedido.EN_COCINA,
       cliente=request.user.cliente
   )
   Cuenta.objects.create(pedido=nuevo_pedido, precio_total=0)

   total_pedido = Decimal('0.0')

   carrito_session = request.session.get('carrito', {})
   for hamburguesa_id, cantidad in carrito_session.items():
       hamburguesa = get_object_or_404(Hamburguesa, id=hamburguesa_id)
       precio_hamburguesa = hamburguesa.precio
       detalle_pedido = DetallePedido.objects.create(
           pedido=nuevo_pedido,
           hamburguesa_id=hamburguesa_id,
           estado=EstadoProducto.EN_ESPERA,
           precio=precio_hamburguesa,
           cantidad=cantidad
       )
       total_pedido += Decimal(str(precio_hamburguesa)) * Decimal(cantidad)

   nuevo_pedido.cuenta.estado_pago = EstadoCuenta.PAGADO
   nuevo_pedido.cuenta.precio_total = total_pedido
   nuevo_pedido.cuenta.save()
   request.session['carrito'] = {}

   return redirect('confirmacion')

@user_passes_test(es_cliente)
def confirmacion(request):
    return render(request, 'confirmacion.html')

@user_passes_test(es_admin)
def nueva_mesa(request):
   if request.method == 'POST':
       form = MesaForm(request.POST)
       if form.is_valid():
           form.save()
           return redirect('camarero')
   else:
       form = MesaForm()


   return render(request, 'form_mesa.html', {'form': form})


@user_passes_test(es_admin)
def editar_mesa(request, id):
   mesa = get_object_or_404(Mesa, id=id)


   if request.method == 'POST':
       form = MesaForm(request.POST, instance=mesa)
       if form.is_valid():
           form.save()
           return redirect('camarero')
   else:
       form = MesaForm(instance=mesa)


   return render(request, 'form_mesa.html', {'form': form})


@user_passes_test(es_admin)
def eliminar_mesa(request, id):
   mesa = get_object_or_404(Mesa, id=id)
   mesa.delete()
   return redirect('camarero')

@user_passes_test(es_admin)
def nueva_hamburguesa(request):
   if request.method == 'POST':
       form = HamburguesaForm(request.POST)
       if form.is_valid():
           form.save()
           return redirect('ir_carta')
   else:
       form = HamburguesaForm()


   return render(request, 'form_hamburguesa.html', {'form': form})

@user_passes_test(es_admin)
def editar_hamburguesa(request, id):
   hamburguesa = get_object_or_404(Hamburguesa, id=id)


   if request.method == 'POST':
       form = HamburguesaForm(request.POST, instance=hamburguesa)
       if form.is_valid():
           form.save()
           return redirect('ir_carta')
   else:
       form = HamburguesaForm(instance=hamburguesa)


   return render(request, 'form_hamburguesa.html', {'form': form})


@user_passes_test(es_admin)
def eliminar_hamburguesa(request, id):
   hamburguesa = get_object_or_404(Hamburguesa, id=id)
   hamburguesa.delete()
   return redirect('ir_carta')

@login_required
def perfil_usuario(request):
   return render(request, 'perfil.html')

@user_passes_test(es_admin)
def pedidos_admin(request):
    pedidos = Pedido.objects.all().prefetch_related(
        'detalles__hamburguesa',
        'detalles__ingredientedetalle_set__ingrediente',
        'cliente',
        'mesa'
    ).order_by('-fecha')

    context = {
        'pedidos': pedidos,
    }
    return render(request, 'pedidos_admin.html', context)

def eliminar_pedido_admin(request, pedido_id):

    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, id=pedido_id)
        pedido.delete()
        return redirect('pedidos_admin')

    return redirect('pedidos_admin')

@user_passes_test(es_cliente)
def pedidos_cliente(request):
   cliente = request.user.cliente
   pedidos = Pedido.objects.filter(cliente=cliente)
   return render(request, 'pedidos_cliente.html', {'pedidos': pedidos})

def analisis_mensual(request):
    reportes = ReporteMensualVentas.objects.all().order_by('-anio', '-mes')
    return render(request, 'analisis_mensual.html', {'reportes': reportes})

def generar_reporte_mensual(request):
    with connection.cursor() as cursor:
        cursor.callproc('GENERAR_REPORTE_MENSUAL')
    return redirect('analisis_mensual')