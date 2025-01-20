import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import plotly.graph_objects as go

# Initialize query parameters once
query_params = st.query_params

# Helper function to get parameter or default value
def get_param(param, default, cast_func=float):
    return cast_func(query_params[param]) if param in query_params else default

# Streamlit App
st.title("Profit and Efficiency Simulator")

# Create columns for sliders
col1, col2 = st.columns(2)

# Sliders with independent states
with col1:
    weekend_multiplier = st.slider(
        "Weekend Multiplier", 1.0, 2.0, get_param("weekend_multiplier", 1.2), 0.05
    )
    production_cost_percentage = st.slider(
        "Production Material Cost Percentage", 0.2, 0.6, get_param("production_cost", 0.3), 0.01
    )
    marketing_fee_percentage = st.slider(
        "Marketing Fee Percentage", 0.0, 0.2, get_param("marketing_fee", 0.15), 0.01
    )

with col2:
    work_cost_percentage = st.slider(
        "Work Cost Percentage", 0.0, 0.6, get_param("work_cost", 0.2), 0.01
    )
    fixed_work_cost = st.slider(
        "Fixed Work Cost Per Day", 0, 500, get_param("fixed_work_cost", 0, int), 10
    )
    workload_scaling_factor_per_1000e = st.slider(
        "Workload Scaling Factor per 1000€", 0.0, 0.1, get_param("workload_scaling", 0.01), 0.0001
    )

# Calculate workload scaling factor
workload_scaling_factor = workload_scaling_factor_per_1000e / 1000  # Scaling factor per €

# Update query parameters only when a button is clicked
if st.button("Save Parameters to URL"):
    st.query_params.from_dict(
        {
            "weekend_multiplier": str(weekend_multiplier),
            "production_cost": str(production_cost_percentage),
            "marketing_fee": str(marketing_fee_percentage),
            "work_cost": str(work_cost_percentage),
            "fixed_work_cost": str(fixed_work_cost),
            "workload_scaling": str(workload_scaling_factor_per_1000e),
        }
    )

# Define the ranges for marketing spend and ROAS
marketing_spend_range = np.linspace(0, 1000, 100)  # Marketing spend from 0€ to 1000€
roas_range = np.linspace(1.0, 8.0, 100)  # ROAS from 1.0 to 8.0

# Create a grid of marketing spend and ROAS
marketing_spend, roas = np.meshgrid(marketing_spend_range, roas_range)

# Calculate revenue and profit
revenue = marketing_spend * roas
production_cost = revenue * production_cost_percentage
marketing_cost = marketing_spend * (1 + marketing_fee_percentage)

# Adjust work cost with workload factor
workload_base_rate = work_cost_percentage + workload_scaling_factor * revenue
workload_factor = revenue * workload_base_rate
work_cost = fixed_work_cost + workload_factor

profit = revenue - production_cost - marketing_cost - work_cost * weekend_multiplier

# Calculate efficiency (Profit per Marketing Spend)
efficiency = np.where(marketing_spend > 0, profit / marketing_spend, 0)

# Efficiency Plot
fig2, ax2 = plt.subplots(figsize=(10, 6))
efficiency_contour = ax2.contourf(marketing_spend, roas, efficiency, cmap='plasma', levels=20)
fig2.colorbar(efficiency_contour, ax=ax2, label='Profit per Marketing Spend (€)')
ax2.set_title('Marketing Efficiency (Profit per Marketing Spend)', fontsize=16)
ax2.set_xlabel('Marketing Spend (€)', fontsize=14)
ax2.set_ylabel('ROAS', fontsize=14)
ax2.contour(marketing_spend, roas, profit, levels=[0], colors='white', linewidths=2, linestyles='solid')
st.pyplot(fig2)

# Plotting profit surface
fig, ax = plt.subplots(subplot_kw={"projection": "3d"}, figsize=(10, 8))
surf = ax.plot_surface(marketing_spend, roas, profit, cmap='viridis', edgecolor='none', alpha=0.8)
ax.contour(marketing_spend, roas, profit, levels=[0], colors='red', linewidths=2, linestyles='solid')
ax.set_title('Profit vs Marketing Spend and ROAS (Workload Adjusted)', fontsize=16)
ax.set_xlabel('Marketing Spend (€)', fontsize=14)
ax.set_ylabel('ROAS', fontsize=14)
ax.set_zlabel('Profit (€)', fontsize=14)
st.pyplot(fig)

# Plotting profit surface with Plotly
fig1 = go.Figure()
fig1.add_trace(go.Surface(z=profit, x=marketing_spend_range, y=roas_range, colorscale='Viridis', opacity=0.8))

fig1.update_layout(
    title="Profit vs Marketing Spend and ROAS (Interactive)",
    scene=dict(
        xaxis_title="Marketing Spend (€)",
        yaxis_title="ROAS",
        zaxis_title="Profit (€)"
    ),
    width=1200,  # Adjust width
    height=800   # Adjust height
)

st.plotly_chart(fig1)
