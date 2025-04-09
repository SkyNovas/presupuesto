import streamlit as st
import pandas as pd
import plotly.express as px

def highlight_second_max(s, color='yellow'):
    '''
    Highlights the second largest value in a Series with a given color.
    '''
    if s.dtype in ['int64', 'float64']:
        second_max = s.nlargest(2).iloc[-1]
        return ['background-color: %s' % color if v == second_max else '' for v in s]
    return [''] * len(s)

def calculate_costs(inputs):
    costs = {}

    # CodeCommit
    users = inputs['codecommit_users']
    costs['CodeCommit'] = max(users - 5, 0) * 1.00

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
    duration_sec = duration * 60
    costs['CodeBuild'] = builds * duration_sec * 0.00002

    # CodeArtifact
    storage = inputs['codeartifact_storage']
    requests = inputs['codeartifact_requests']
    intra = inputs['codeartifact_intra']
    outbound = inputs['codeartifact_outbound']

    # Cálculos con free tier
    storage_cost = max(storage - 2, 0) * 0.05
    requests_cost = max(requests - 100000, 0) * 0.000005
    intra_cost = intra * 0.02
    outbound_cost = outbound * 0.09

    costs['CodeArtifact'] = storage_cost + requests_cost + intra_cost + outbound_cost
    costs['CodeArtifact'] = costs['CodeArtifact'] + 0.60

    # CodeDeploy
    instances = inputs['codedeploy_instances']
    deployments = inputs['codedeploy_deployments']
    costs['CodeDeploy'] = instances * deployments * 0.02

    return costs

st.set_page_config(page_title="AWS Cost Calculator", layout="wide")
st.title("Calculadora de Costos AWS 📊")
st.markdown("---")

# --- Selección de entornos para comparar ---
st.header("🔍 Comparación de Entornos")
environments = ["Producción", "Desarrollo (DEV)", "Pruebas (UAT)", "QA"]
selected_environments = st.multiselect(
    "Seleccionar Entornos a Comparar",
    environments,
    default=environments,
    help="Selecciona los entornos que deseas comparar"
)
st.markdown("---")

# Sidebar para configuraciones de entornos
with st.sidebar:
    st.header("⚙️ Configuración de Entornos")
    environment_inputs = {}
    for env in environments:
        with st.expander(f"Configuración {env}"):
            environment_inputs[env] = {
                'codecommit_users': st.number_input(
                    f"{env} - CodeCommit - Usuarios activos", 0, 10000,
                    125 if env == "Producción" else (
                    500 if env == "Desarrollo (DEV)" else (
                    125 if env == "Pruebas (UAT)" else 250)),
                    help="Primeros 5 usuarios gratuitos", key=f"{env}_codecommit_users"),
                
                'codepipeline_v1': st.number_input(
                    f"{env} - CodePipeline V1 - Pipelines activos", 0, 50000, 0,
                    help="Primer pipeline gratuito", key=f"{env}_codepipeline_v1"),
                
                'codepipeline_v2': st.number_input(
                    f"{env} - CodePipeline V2 - Minutos ejecución", 0, 100000,
                    25000 if env == "Producción" else (
                    100000 if env == "Desarrollo (DEV)" else (
                    25000 if env == "Pruebas (UAT)" else 50000)),
                    help="Primeros 100 minutos gratuitos", key=f"{env}_codepipeline_v2"),
                
                'codeguru_repos': st.number_input(
                    f"{env} - CodeGuru - Repositorios", 1, 5000,
                    125 if env == "Producción" else (
                    500 if env == "Desarrollo (DEV)" else (
                    125 if env == "Pruebas (UAT)" else 250)),
                    help="Número de repositorios analizados", key=f"{env}_codeguru_repos"),
                
                'codeguru_lines': st.number_input(
                    f"{env} - CodeGuru - Líneas/repositorio", 1, 1000000, 10000,
                    help="Líneas de código por repositorio", key=f"{env}_codeguru_lines"),
                
                'codebuild_builds': st.number_input(
                    f"{env} - CodeBuild - Builds/mes", 0, 10000000,
                    25000 if env == "Producción" else (
                    100000 if env == "Desarrollo (DEV)" else (
                    25000 if env == "Pruebas (UAT)" else 50000)),
                    help="Número total de builds mensuales", key=f"{env}_codebuild_builds"),
                
                'codebuild_duration': st.number_input(
                    f"{env} - CodeBuild - Duración (min)", 0, 600, 5,
                    help="Duración promedio por build", key=f"{env}_codebuild_duration"),
                
                'codeartifact_storage': st.number_input(
                    f"{env} - CodeArtifact - Almacenamiento (GB)", 0, 1000, 100,
                    help="Primeros 2 GB gratuitos", key=f"{env}_codeartifact_storage"),
                
                'codeartifact_requests': st.number_input(
                    f"{env} - CodeArtifact - Solicitudes/mes", 0, 10000000,
                    25000 if env == "Producción" else (
                    100000 if env == "Desarrollo (DEV)" else (
                    25000 if env == "Pruebas (UAT)" else 50000)),
                    help="Primeras 100,000 solicitudes gratuitas", key=f"{env}_codeartifact_requests"),
                
                'codeartifact_intra': st.number_input(
                    f"{env} - Transferencia Intra (GB)", 0.0, 10000.0, 0.0,
                    help="0.01 USD/GB entrada + 0.01 USD/GB salida", key=f"{env}_codeartifact_intra"),
                
                'codeartifact_outbound': st.number_input(
                    f"{env} - Transferencia Saliente (GB)", 0.0, 10000.0, 100.0,
                    help="0.09 USD/GB a Internet", key=f"{env}_codeartifact_outbound"),
                
                'codedeploy_instances': st.number_input(
                    f"{env} - CodeDeploy - Instancias", 0, 1000, 1,
                    help="Número de instancias desplegadas", key=f"{env}_codedeploy_instances"),
                
                'codedeploy_deployments': st.number_input(
                    f"{env} - CodeDeploy - Despliegues/mes", 0, 1000000,
                    25000 if env == "Producción" else (
                    100000 if env == "Desarrollo (DEV)" else (
                    25000 if env == "Pruebas (UAT)" else 50000)),
                    help="Despliegues mensuales por instancia", key=f"{env}_codedeploy_deployments")
            }

# Calcular costos para cada entorno
environment_costs = {}
for env, inputs in environment_inputs.items():
    environment_costs[env] = calculate_costs(inputs)

if selected_environments:
    st.header("Comparativa de Costos Seleccionados")

    # --- Métricas Clave ---
    st.subheader("Métricas Clave Comparativas")
    metrics_data = {}
    for env in selected_environments:
        if env in environment_costs:
            total_cost = sum(environment_costs[env].values())
            most_expensive = max(environment_costs[env], key=environment_costs[env].get) if environment_costs[env] else "N/A"
            max_individual = max(environment_costs[env].values()) if environment_costs[env] else "N/A"
            metrics_data[env] = {
                "Costo Total Mensual": f"${total_cost:,.2f} USD",
                "Servicio Más Costoso": most_expensive,
                "Costo Máximo Individual": f"${max_individual:,.2f} USD",
            }
    metrics_df = pd.DataFrame(metrics_data).T
    st.dataframe(metrics_df)
    st.markdown("---")

    # --- Desglose Detallado con Totales ---
    st.subheader("Desglose Detallado Comparativo")
    detailed_data = {}
    totals = {env: 0.0 for env in selected_environments}
    
    for env in selected_environments:
        if env in environment_costs:
            for service, cost in environment_costs[env].items():
                if service not in detailed_data:
                    detailed_data[service] = {}
                detailed_data[service][env] = f"${cost:,.2f}"
                totals[env] += cost
    
    # Agregar fila de totales
    detailed_data['Total'] = {env: f"${totals[env]:,.2f}" for env in selected_environments}
    
    detailed_df = pd.DataFrame(detailed_data).T
    st.dataframe(detailed_df)
    st.markdown("---")

    # --- Visualizaciones ---
    st.subheader("Visualizaciones Comparativas")
    cols = st.columns(len(selected_environments))
    for i, env in enumerate(selected_environments):
        with cols[i]:
            st.subheader(env)
            df_viz = pd.DataFrame(list(environment_costs[env].items()), columns=['Servicio', 'Costo'])
            
            fig_bar = px.bar(df_viz, x='Servicio', y='Costo', color='Servicio',
                            title="Distribución de Costos", text_auto='.2s')
            st.plotly_chart(fig_bar, use_container_width=True)
            
            fig_pie = px.pie(df_viz, names='Servicio', values='Costo',
                            title="Distribución Porcentual", hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown("---")

else:
    st.info("Por favor, selecciona al menos un entorno para comparar.")

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
    Costo = Builds × Duración × 0.00002 USD
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