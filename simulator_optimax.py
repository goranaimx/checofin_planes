import math

class CalculadoraAllianzOptimax:
    def __init__(self, edad_actual, aportacion_mensual, edad_retiro=65, 
                 rendimiento_anual=0.10, inflacion_anual=0.05, sueldo_mensual_bruto=50000):
        """
        Simulador de PPR Allianz Optimax Plus basado en la estructura de cargos estándar.
        """
        self.edad_actual = edad_actual
        self.edad_retiro = edad_retiro
        self.aportacion_mensual = aportacion_mensual
        self.rendimiento_mensual = (1 + rendimiento_anual)**(1/12) - 1
        self.inflacion_mensual = (1 + inflacion_anual)**(1/12) - 1
        self.sueldo_mensual_bruto = sueldo_mensual_bruto
        
        # Parámetros Allianz (Valores estándar aproximados)
        self.meses_fondo_inicial = 18
        self.cargo_gestion_anual = 0.015  # 1.5% anual sobre saldo total
        self.cargo_fijo_mensual_udis = 20 # Aprox 20 USD/UDIs mensuales indexados
        self.cargo_fondo_inicial_mensual = 0.006 # 0.6% mensual (7.2% anual) sobre el Fondo Inicial
        self.bono_fidelidad_pct = 0.35 # Varía según plazo, 35% es común para 25 años
        
    def simular(self):
        meses_totales = (self.edad_retiro - self.edad_actual) * 12
        
        fondo_inicial = 0
        fondo_acumulacion = 0
        total_aportado = 0
        total_beneficio_fiscal = 0
        
        # Bono de fidelidad (se aplica sobre la aportación del primer año)
        bono_inicial = (self.aportacion_mensual * 12) * self.bono_fidelidad_pct
        fondo_inicial += bono_inicial
        
        for mes in range(1, meses_totales + 1):
            # Ajuste de aportación por inflación (cada 12 meses)
            if mes > 1 and mes % 12 == 1:
                self.aportacion_mensual *= (1 + (self.inflacion_mensual * 12))
            
            # Distribución de aportación
            if mes <= self.meses_fondo_inicial:
                fondo_inicial += self.aportacion_mensual
            else:
                fondo_acumulacion += self.aportacion_mensual
            
            total_aportado += self.aportacion_mensual
            
            # Aplicar Rendimientos
            fondo_inicial *= (1 + self.rendimiento_mensual)
            fondo_acumulacion *= (1 + self.rendimiento_mensual)
            
            # Aplicar Cargos
            # 1. Cargo sobre Fondo Inicial (0.6% mensual)
            fondo_inicial -= (fondo_inicial * self.cargo_fondo_inicial_mensual)
            
            # 2. Cargo de Gestión (1.5% anual / 12)
            cargo_gestion = (fondo_inicial + fondo_acumulacion) * (self.cargo_gestion_anual / 12)
            fondo_acumulacion -= cargo_gestion
            
            # 3. Cargo Fijo (indexado a inflación)
            cargo_fijo = self.cargo_fijo_mensual_udis * (1 + self.inflacion_mensual)**mes
            fondo_acumulacion -= cargo_fijo
            
            # Cálculo de Beneficio Fiscal (Anual - Art 151 LISR)
            # Deducción max: 10% ingreso anual o 5 UMAs (aprox $189k)
            if mes % 12 == 0:
                aportado_anio = self.aportacion_mensual * 12
                limite_deduccion = min(self.sueldo_mensual_bruto * 12 * 0.10, 189000)
                deducido = min(aportado_anio, limite_deduccion)
                # Asumiendo tasa impositiva marginal del 30% (promedio para este perfil)
                total_beneficio_fiscal += (deducido * 0.30)

        saldo_final = max(0, fondo_inicial + fondo_acumulacion)
        
        return {
            "Edad Retiro": self.edad_retiro,
            "Total Aportado": round(total_aportado, 2),
            "Saldo Final Estimado": round(saldo_final, 2),
            "Beneficio Fiscal Acumulado (SAT)": round(total_beneficio_fiscal, 2),
            "Plusvalía Neta": round(saldo_final - total_aportado, 2)
        }

# --- EJEMPLO DE USO ---
simulador = CalculadoraAllianzOptimax(
    edad_actual=35, 
    aportacion_mensual=5000, 
    rendimiento_anual=0.10, # Escenario moderado/alto (Equity)
    sueldo_mensual_bruto=60000
)

resultados = simulador.simular()

print("--- RESULTADOS PPR ALLIANZ OPTIMAX ---")
for k, v in resultados.items():
    print(f"{k}: ${v:,.2f}" if isinstance(v, float) else f"{k}: {v}")
