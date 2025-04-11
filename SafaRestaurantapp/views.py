from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from SafaRestaurantapp.forms import *
from SafaRestaurantapp.models import Camarero, Hamburguesa, Ingrediente, Cocinero, TareaCocina, TipoCocinero, \
    DetallePedido, Pedido, IngredienteDetalle


# ============================ PÁGINAS ESTÁTICAS ============================

def go_home_page(request):
    return render(request, 'home.html')

def go_about_us(request):
    return render(request, 'about_us.html')

def go_rol_page(request):
    return render(request, 'rol.html')

def go_register(request):
    return render(request, 'register.html')

# ============================ VISTAS POR ROL ============================

def go_cliente_view(request):
    return render(request, 'cliente.html')

def go_camarero_view(request):
    return render(request, 'camarero.html')

def go_cocinero_view(request):
    return render(request, 'cocinero.html')

def go_adminn_view(request):
    return render(request, 'adminn.html')

# ============================ SEGURIDAD ============================

def go_seguridad_admin(request):
    return render(request, 'seguridad_admin.html')

def go_seguridad_camarero(request):
    return render(request, 'seguridad_camarero.html')

# ============================ CAMAREROS ============================

def formulario_camarero(request):
    return render(request, 'formulario_camarero.html')

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


def cargar_listado_camareros(request):
    lista_camareros = Camarero.objects.all()
    return render(request, 'admin.html', {'camareros': lista_camareros})

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
            pedido = Pedido.objects.create()
            request.session['pedido_id'] = pedido.id

        detalle = DetallePedido.objects.create(pedido=pedido, hamburguesa=hamburguesa)

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

def cargar_listado_cocineros(request):
    cocineros = Cocinero.objects.prefetch_related('tareas').all()

    return render(request, 'cocineros.html', {
        'cocineros': cocineros
    })

def formulario_cocinero(request):
    return render(request, 'formulario_cocinero.html')


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



