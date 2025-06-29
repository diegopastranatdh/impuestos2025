from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from estructura_embebida import estructura

#import json
#import os
#import pandas as pd
#import requests

#def hay_nueva_version(version_actual):
 #   try:
  #      r = requests.get("https://tuservidor.com/version.txt")
   #     if r.status_code == 200:
    #        version_online = r.text.strip()
     #       return version_online != version_actual
    #except:
     #   pass
    #return False 

#ruta_json = os.path.join(os.path.dirname(__file__), "estructura_impuestos.json")
#with open(ruta_json, "r", encoding="utf-8") as f:
#    estructura = json.load(f)


#def cargar_estructura_desde_excel(ruta_excel, uvt=47065):
 #   df = pd.read_excel(ruta_excel)
   
   # LIMPIAR LOS ENCABEZADOS para evitar errores por espacios o mayúsculas
  #  df.columns = [col.strip() for col in df.columns]

    # (OPCIONAL: imprimir los nombres reales de las columnas para verificar)
    #print("ENCABEZADOS ENCONTRADOS:", df.columns.tolist())
    #estructura = {}
    #for _, row in df.iterrows():
     #   ciudad = str(row["Ciudad"]).strip()
      #  tipo = str(row["Concepto"]).strip().lower()
       # actividad = str(row["Actividad"]).strip()
        #tarifa = float(str(row["Tarifa ICA"]).replace("X1000", "")) / 1000
        #base_ica = int(float(row["Base ICA UVT"]) * uvt)
        #rf_declarante = float(str(row["Tarifa RF Declarante"]).replace("%", "")) / 100
        #rf_no_declarante = float(str(row["Tarifa RF No Declarante"]).replace("%", "")) / 100
        #base_rf = int(float(row["Base RF UVT"]) * uvt)

        #estructura.setdefault(ciudad, {}).setdefault(tipo, {})[actividad] = {
         #   "tarifa": tarifa,
          #  "base": base_ica,
           # "retencion_fuente": {
            #    "tarifa_declarante": rf_declarante,
             #   "tarifa_no_declarante": rf_no_declarante,
              #  "base_compras": base_rf,
               # "base_servicios": base_rf
            #}
        #}#
   # return estructura

# Ruta al archivo Excel
#ruta_excel = os.path.join(os.path.dirname(__file__), "estructura_impuestos.xlsx")
#estructura = cargar_estructura_desde_excel(ruta_excel)



class ImpuestoLayout(BoxLayout):
    def formatear_miles(self, instance, value):
    # Evita formato si está vacío o ya tiene coma decimal
        texto = value.replace(",", "").replace(".", "")
        if not texto.isdigit():
            return
        numero = int(texto)
        instance.text = f"{numero:,}".replace(",", ".")  # cambia coma por punto

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=10, **kwargs)

        # --- Sección 0: valor de la operacion de inicio ---

        seccion_valor = BoxLayout(orientation='vertical', size_hint_y=None, height='60dp')
        self.valor_input = TextInput(hint_text='Valor de la operación', input_filter='float', multiline=False)
        self.valor_input.bind(text=self.formatear_miles)
        seccion_valor.add_widget(self.valor_input)
    
    # --- Sección 1: Tipo, ciudad y actividad ---
        seccion_ubicacion = BoxLayout(orientation='vertical', spacing=5)
        self.tipo_spinner = Spinner(text='Seleccione tipo', values=['compras', 'servicios'])
        self.tipo_spinner.bind(text=self.on_tipo_selected)
        self.ciudad_spinner = Spinner(text='Seleccione ciudad', values=sorted(estructura.keys()), disabled=True)
        self.ciudad_spinner.bind(text=self.on_ciudad_selected)
        self.actividad_spinner = Spinner(text='Seleccione actividad', values=[], disabled=True)
        seccion_ubicacion.add_widget(self.tipo_spinner)
        seccion_ubicacion.add_widget(self.ciudad_spinner)
        seccion_ubicacion.add_widget(self.actividad_spinner)


        # ---- seccion 2: Coperativas o Regimen Simple
        seccion_regimensimple = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', spacing=10)
        self.cooperativa_spinner = Spinner(
            text='¿Es Cooperativa?', 
            values=['Sí', 'No'], 
            disabled=True,
             size_hint=(1, None),
            height='40dp'
            )
        self.cooperativa_spinner.bind(text=self.bloquear_cooperativa)

        self.regimen_simple_spinner = Spinner(
            text='¿Es Regimen Simple?', 
            values=['Sí', 'No'], 
            disabled=True,
            size_hint=(1, None),
            height='40dp'
            )
        self.regimen_simple_spinner.bind(text=self.bloquear_regimen_simple)
        seccion_regimensimple.add_widget(self.cooperativa_spinner)
        seccion_regimensimple.add_widget(self.regimen_simple_spinner)




        # --- Sección 3: Datos del declarante ---
        seccion_declarante = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', spacing=10)
        self.declarante_spinner = Spinner(
            text='¿Es Declarante de Renta?', 
            values=['Sí', 'No'], 
            disabled=True,
             size_hint=(1, None),
            height='40dp'
            )
        self.declarante_spinner.bind(text=self.bloquear_declarante_renta)
        self.declarante_iva_spinner = Spinner(
            text='¿Es Declarante de IVA?', 
            values=['Sí', 'No'], 
            disabled=True,
            size_hint=(1, None),
            height='40dp'
            )
        self.declarante_iva_spinner.bind(text=self.bloquear_declarante_iva)
        
        self.incluye_iva = Spinner(
            text='IVA Incluido?', 
            values=['Sí', 'No'], 
            disabled=True,
            size_hint_y=None,
            height='45dp')

        self.incluye_iva.bind(text=self.bloquear_incluye_iva)

        seccion_declarante.add_widget(self.declarante_spinner)
        seccion_declarante.add_widget(self.declarante_iva_spinner)
        seccion_declarante.add_widget(self.incluye_iva)
        
        # --- Sección 4: Valor operación y cálculo ---
        seccion_valores = BoxLayout(orientation='vertical', spacing=5)
        self.resultado = Label(text='', size_hint_y=None, height='150dp')
        self.calcular_btn = Button(text='Calcular', disabled=True, size_hint_y=None, height='40dp')
        self.calcular_btn.bind(on_press=self.calcular)

    
        seccion_valores.add_widget(self.calcular_btn)
        seccion_valores.add_widget(self.resultado)

        # --- Sección 5: Botones finales ---
        seccion_botones = BoxLayout(size_hint_y=None, height='40dp', spacing=10)
        self.limpiar_btn = Button(text='Limpiar')
        self.limpiar_btn.bind(on_press=self.limpiar)
        self.cerrar_btn = Button(text='Cerrar aplicación')
        self.cerrar_btn.bind(on_press=lambda x: App.get_running_app().stop())

        seccion_botones.add_widget(self.limpiar_btn)
        seccion_botones.add_widget(self.cerrar_btn)


        # Luego agregas el resto de las secciones
        self.add_widget(seccion_valor)       # ⬆ VALOR primero
        self.add_widget(seccion_ubicacion)
        self.add_widget(seccion_regimensimple)
        self.add_widget(seccion_declarante)
        self.add_widget(seccion_valores)
        self.add_widget(seccion_botones)

    def on_tipo_selected(self, spinner, text):
        self.tipo_spinner.disabled = True
        self.ciudad_spinner.disabled = False

    def on_ciudad_selected(self, spinner, text):
        self.ciudad_spinner.disabled = True
        tipo = self.tipo_spinner.text
        ciudad = self.ciudad_spinner.text  # ✅ Ya no se usa upper()
        actividades = estructura.get(ciudad, {}).get(tipo, {})
        self.actividad_spinner.values = sorted(actividades.keys())
        self.actividad_spinner.disabled = False
        self.actividad_spinner.bind(text=self.on_actividad_selected)
        self.valor_input.disabled = False


    def on_actividad_selected(self, spinner, text):
        self.actividad_spinner.disabled = True
        self.valor_input.disabled = False
        self.declarante_spinner.disabled = False
                # -- self.incluye_iva.disabled = False
        self.calcular_btn.disabled = False
        
         # Activar solo "¿Es Cooperativa?"
        self.cooperativa_spinner.disabled = False

         # Desactivar y reiniciar los demás
        self.regimen_simple_spinner.text = "¿Es Regimen Simple?"
        self.regimen_simple_spinner.disabled = True

        self.declarante_spinner.text = '¿Es Declarante de Renta?'
        self.declarante_spinner.disabled = True

        self.declarante_iva_spinner.text = '¿Es Declarante de IVA?'
        self.declarante_iva_spinner.disabled = True

        self.incluye_iva.text = '¿IVA Incluido?'
        self.incluye_iva.disabled = True

        
    def bloquear_cooperativa(self, spinner, text):
        self.cooperativa_spinner.disabled = True

        if text == 'No':
            self.regimen_simple_spinner.disabled= False
            self.declarante_iva_spinner.text = '¿Es Declarante de IVA?'
            self.declarante_spinner.disabled = True

            self.incluye_iva.text = '¿IVA Incluido?'
            self.incluye_iva.disabled = True
        else:
             self.regimen_simple_spinner.text = "¿Es Regimen Simple?" 
             self.regimen_simple_spinner.disabled = True
             
             self.declarante_spinner.text = 'No'
             self.declarante_spinner.disabled = True

             self.declarante_iva_spinner.text = '¿Es Declarante de IVA?'
             self.declarante_iva_spinner.disabled = False

             self.incluye_iva.text = 'IVA Incluido?'
             self.incluye_iva.disabled = True

    def bloquear_regimen_simple(self, spinner, text):

        self.regimen_simple_spinner.disabled = True
        if text == 'No':
            self.regimen_simple_spinner.text = "¿Es Regimen Simple?" 
            self.regimen_simple_spinner.disabled = True
            
            self.declarante_spinner.text = '¿Es Declarate de Renta?'
            self.declarante_spinner.disabled = False
        else:
            self.incluye_iva.text = "IVA Incluido?"    
            self.incluye_iva.disabled = True

            self.declarante_iva_spinner.text = '¿Es Declarante de IVA?'
            self.declarante_iva_spinner.disabled = False


    def bloquear_declarante_renta(self, spinner, text):
        self.declarante_spinner.disabled = True

    def bloquear_declarante_iva(self, spinner, text):
        self.declarante_iva_spinner.disabled = True

        if text == 'No':
            self.incluye_iva.text = 'No'
            self.incluye_iva.disabled = True
        else:
        # Si es declarante de IVA, habilita el campo
            self.incluye_iva.disabled = False

    def bloquear_incluye_iva(self, spinner, text):
        self.incluye_iva.disabled = True
        if text == 'Sí':
            self.incluye_iva.disabled = False
        else:
            self.incluye_iva.text = 'IVA Incluido?' 
            self.incluye_iva.disabled = True

    def limpiar(self, instance):
        self.tipo_spinner.text = 'Seleccione Tipo'
        self.tipo_spinner.disabled = False

        self.ciudad_spinner.text = 'Seleccione Ciudad'
        self.ciudad_spinner.disabled = True

        self.actividad_spinner.text = 'Seleccione Actividad'
        self.actividad_spinner.disabled = True

        self.valor_input.text = ''
        self.valor_input.disabled = True

        self.resultado.text = ''
        self.calcular_btn.disabled = True

        self.incluye_iva.text = 'IVA Incluido?'
        self.incluye_iva.disabled = True

        
        self.valor_input.text = ''
        self.valor_input.disabled = False

        self.cooperativa_spinner.text = "¿Es Cooperativa?"
        self.cooperativa_spinner.disabled = True

        self.regimen_simple_spinner.text = "¿Es Regimen Simple?"
        self.regimen_simple_spinner.disabled = True

        self.declarante_spinner.text = '¿Es Declarante de Renta?'
        self.declarante_spinner.disabled = True

        self.declarante_iva_spinner.text = '¿Es Declarante de IVA?'
        self.declarante_iva_spinner.disabled = True

        self.regimen_simple_spinner.text = "¿Es Regimen Simple?" 
        self.regimen_simple_spinner.disabled = True

        self.incluye_iva.text = "¿IVA Incluido?" 
        self.incluye_iva.disabled = True


    def calcular(self, instance):
        try:
            valor = float(self.valor_input.text.replace(".", "").replace(",", "").strip())
            if not self.valor_input.text.strip().replace(".", "").isdigit():
                self.resultado.text = "Por favor ingrese un valor válido para la operación."
                return

            tipo = self.tipo_spinner.text
            ciudad = self.ciudad_spinner.text
            actividad = self.actividad_spinner.text
            incluido = self.incluye_iva.text == 'Sí'
            declarante = self.declarante_spinner.text == 'Sí'
            declarante_iva = self.declarante_iva_spinner.text == 'Sí'

            if incluido:
                base = valor / 1.19
                iva = valor - base
                valor_con_iva = valor
            else:
                base = valor
                iva = valor * 0.19 if declarante_iva else 0
                valor_con_iva = valor + iva

            datos = estructura.get(ciudad, {}).get(tipo, {}).get(actividad)
            if not datos:
                self.resultado.text = "No se encontró la actividad seleccionada."
                return

            rf = datos.get('retencion_fuente', {})
            base_min_rf = rf.get('base_compras', 0) if tipo == 'compras' else rf.get('base_servicios', 0)
            es_cooperativa = self.cooperativa_spinner.text == 'Sí'
            es_regimen_simple = self.regimen_simple_spinner.text == 'Sí'

            if not es_cooperativa and not es_regimen_simple:
                tarifa_rf = rf.get('tarifa_declarante', 0) if declarante else rf.get('tarifa_no_declarante', 0)
                retefuente = tarifa_rf * base if base >= base_min_rf else 0
            else:
                tarifa_rf = 0
                retefuente = 0

            actividad_lower = actividad.lower()
            if "compra de combustible" in actividad_lower:
                reteiva = 0
                iva = 0
            elif declarante_iva:
                reteiva = 0.15 * iva if base >= base_min_rf else 0
            else:
                reteiva = 0
                iva = 0

            if not es_regimen_simple:
                tarifa = datos['tarifa']
                base_min = datos.get('base', 0)
                reteica = base * tarifa if base >= base_min else 0
            else:
                reteica = 0

            # ✅ Calcular sobretasa y avisos solo si reteica > 0
            if reteica > 0:
                tarifa_sobretasa = datos.get('tarifa_sobretasa', 0)
                sobretasa = reteica * tarifa_sobretasa

                tarifa_avisos = datos.get('tarifa_avisos', 0)
                avisos_tableros = reteica * tarifa_avisos
            else:
                sobretasa = 0
                avisos_tableros = 0

            total_ret = retefuente + reteiva + reteica + sobretasa + avisos_tableros
            total_pago = valor_con_iva - total_ret

            self.resultado.text = (
                f"Base: ${base:,.2f}\n"
                f"IVA: ${iva:,.2f}\n"
                f"Ret. Fuente: ${retefuente:,.2f}\n"
                f"Tarifa RF aplicada: {tarifa_rf*100:.2f}%\n"
                f"ReteIVA: ${reteiva:,.2f}\n"
                f"ReteICA: ${reteica:,.2f}\n"
                f"Sobretasa: ${sobretasa:,.2f}\n"
                f"Avisos y Tableros: ${avisos_tableros:,.2f}\n"
                f"Total a pagar: ${total_pago:,.2f}"
            )

        except Exception as e:
            self.resultado.text = f"Error: {str(e)}"


class ImpuestoApp(App):
    def build(self):
        return ImpuestoLayout()


if __name__ == '__main__':
    ImpuestoApp().run()
