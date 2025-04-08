import streamlit as st
import pandas as pd
import plotly.express as px

def calculate_costs(inputs):
    costs = {}
    
    # CodeCommit
    users = inputs['codecommit_users']
    costs['CodeCommit'] = max(users - 5, 0) * 1.00  # 5 usuarios gratis
    
    # CodePipeline
    v1_pipelines = inputs['codepipeline_v1']
    v2_minutes = inputs['codepipeline_v2']
    costs['CodePipeline'] = max(v1_pipelines - 1, 0)*1.00 + max(v2_minutes - 100, 0)*0.002
    
    # CodeGuru
    repos = inputs['codeguru_repos']
    lines_per_repo = inputs['codeguru_lines']
    total_lines = repos * lines_per_repo
    tiers = max((total_lines // 100000) + (1 if total_lines % 100000 > 0 else 0), 1)
    costs['CodeGuru'] = 10.00 + max(tiers - 1, 0) * 30.00
    
    # CodeBuild
    builds = inputs['codebuild_builds']
    duration = inputs['codebuild_duration']
    costs['CodeBuild'] = builds * duration * 0.09  # 0.09 USD/min
    
    # CodeArtifact
    storage = inputs['codeartifact_storage']
    requests = inputs['codeartifact_requests']
    intra = inputs['codeartifact_intra']
    outbound = inputs['codeartifact_outbound']
    
    # Cálculos con free tier
    storage_cost = max(storage - 2, 0) * 0.05  # 2 GB gratis
    requests_cost = max(requests - 100000, 0) * 0.000005  # 100k requests gratis
    intra_cost = intra * 0.02  # 0.01 entrada + 0.01 salida
    outbound_cost = outbound * 0.09
    
    costs['CodeArtifact'] = storage_cost + requests_cost + intra_cost + outbound_cost
    
    # CodeDeploy
    instances = inputs['codedeploy_instances']
    deployments = inputs['codedeploy_deployments']
    costs['CodeDeploy'] = instances * deployments * 0.02
    
    return costs

# Configuración de la interfaz
st.set_page_config(page_title="AWS Cost Calculator", layout="wide")
st.title("Calculadora de Costos AWS 📊")
st.markdown("---")

# Sidebar con inputs
with st.sidebar:
    st.header("⚙️ Configuración de Servicios")
    
    inputs = {
        # CodeCommit
        'codecommit_users': st.number_input(
            "CodeCommit - Usuarios activos", 
            0, 1000, 500,
            help="Primeros 5 usuarios gratuitos"
        ),
        
        # CodePipeline
        'codepipeline_v1': st.number_input(
            "CodePipeline V1 - Pipelines activos", 
            0, 500, 0,
            help="Primer pipeline gratuito"
        ),
        'codepipeline_v2': st.number_input(
            "CodePipeline V2 - Minutos ejecución", 
            0, 100000, 0,
            help="Primeros 100 minutos gratuitos"
        ),
        
        # CodeGuru
        'codeguru_repos': st.number_input(
            "CodeGuru - Repositorios", 
            1, 500, 1,
            help="Número de repositorios analizados"
        ),
        'codeguru_lines': st.number_input(
            "CodeGuru - Líneas/repositorio", 
            1, 1000000, 1000,
            help="Líneas de código por repositorio"
        ),
        
        # CodeBuild
        'codebuild_builds': st.number_input(
            "CodeBuild - Builds/mes", 
            0, 100000, 1,
            help="Número total de builds mensuales"
        ),
        'codebuild_duration': st.number_input(
            "CodeBuild - Duración (min)", 
            1, 600, 10,
            help="Duración promedio por build"
        ),
        
        # CodeArtifact
        'codeartifact_storage': st.number_input(
            "CodeArtifact - Almacenamiento (GB)", 
            0, 1000, 100,
            help="Primeros 2 GB gratuitos"
        ),
        'codeartifact_requests': st.number_input(
            "CodeArtifact - Solicitudes/mes", 
            0, 10000000, 100000,
            help="Primeras 100,000 solicitudes gratuitas"
        ),
        'codeartifact_intra': st.number_input(
            "Transferencia Intra (GB)", 
            0.0, 10000.0, 0.0,
            help="0.01 USD/GB entrada + 0.01 USD/GB salida"
        ),
        'codeartifact_outbound': st.number_input(
            "Transferencia Saliente (GB)", 
            0.0, 10000.0, 100.0,
            help="0.09 USD/GB a Internet"
        ),
        
        # CodeDeploy
        'codedeploy_instances': st.number_input(
            "CodeDeploy - Instancias", 
            0, 1000, 0,
            help="Número de instancias desplegadas"
        ),
        'codedeploy_deployments': st.number_input(
            "CodeDeploy - Despliegues/mes", 
            0, 100000, 0,
            help="Despliegues mensuales por instancia"
        )
    }

# Cálculos
costs = calculate_costs(inputs)
total = sum(costs.values())

# Métricas principales
st.markdown("### 📈 Métricas Clave")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Costo Total Mensual", f"${total:,.2f} USD")
with col2:
    st.metric("Servicio Más Costoso", max(costs, key=costs.get))
with col3:
    st.metric("Costo Máximo Individual", f"${max(costs.values()):,.2f} USD")

# Gráficos
st.markdown("---")
st.markdown("### 📊 Visualización de Costos")
df = pd.DataFrame(list(costs.items()), columns=['Servicio', 'Costo'])

col1, col2 = st.columns(2)
with col1:
    fig = px.bar(df, x='Servicio', y='Costo', color='Servicio',
                title="Distribución de Costos por Servicio",
                text_auto='.2s',
                labels={'Costo': 'USD', 'Servicio': ''})
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig_pie = px.pie(df, names='Servicio', values='Costo', 
                    title="Distribución Porcentual",
                    hole=0.4,
                    )
    st.plotly_chart(fig_pie, use_container_width=True)

# Tabla detallada
st.markdown("---")
st.markdown("### 📋 Desglose Detallado")

highlight_columns = ['Costo', 'Costo Anual']

df['Costo Anual'] = df['Costo'] * 12
st.dataframe(
    df.style.format({
        'Costo': '${:,.2f}',
        'Costo Anual': '${:,.2f}'
    })
    .highlight_max(subset=highlight_columns, color='#FF0000')
    .highlight_min(subset=highlight_columns, color='#90EE90'),
    use_container_width=True,
    height=400
)

# Explicación de cálculos
with st.expander("🧮 Detalles de Cálculo"):
    st.markdown("""
    **CodeCommit:**
    ```python
    Costo = max(Usuarios - 5, 0) × 1.00 USD
    ```
    
    **CodePipeline:**
    ```python
    V1 Costo = max(Pipelines - 1, 0) × 1.00 USD
    V2 Costo = max(Minutos - 100, 0) × 0.002 USD
    ```
    
    **CodeGuru:**
    ```python
    Tiers = Líneas Totales / 100,000 (redondeado arriba)
    Costo = 10.00 USD + (Tiers - 1) × 30.00 USD
    ```
    
    **CodeBuild:**
    ```python
    Costo = Builds × Duración × 0.09 USD
    ```
    
    **CodeArtifact:**
    ```python
    Almacenamiento = max(GB - 2, 0) × 0.05 USD
    Solicitudes = max(Requests - 100,000, 0) × 0.000005 USD
    Transferencia = (Intra × 0.02 USD) + (Outbound × 0.09 USD)
    ```
    
    **CodeDeploy:**
    ```python
    Costo = Instancias × Despliegues × 0.02 USD
    ```
    """)

st.markdown("---")
st.markdown("_* Los precios están basados en la región US East (N. Virginia)_")

# Instrucciones para ejecutar
with st.expander("🚀 Cómo Ejecutar la Aplicación"):
    st.markdown("""
    1. Instalar dependencias:
    ```bash
    pip install streamlit pandas plotly
    ```
    
    2. Ejecutar la aplicación:
    ```bash
    streamlit run app.py --server.port 8501 --server.address 0.0.0.0
    ```
    
    3. Acceder desde:
    ```
    http://localhost:8501
    ```
    """)