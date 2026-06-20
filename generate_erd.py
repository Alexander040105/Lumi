#!/usr/bin/env python3
"""Generate a PNG ERD diagram for the LUMI database schema using matplotlib."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

OUTPUT_PATH = 'd:/63947/Documents/GitHub/Lumi/lumi_erd.png'

# Color scheme per domain
COLORS = {
    'geo': '#4A90E2',
    'renewable': '#5CB85C',
    'stats': '#F0AD4E',
    'user': '#D9534F',
    'auth': '#6C757D',
    'cache': '#9B59B6',
}

def draw_table(ax, x, y, title, columns, color, width=2.4, col_height=0.18, title_height=0.35):
    """Draw a table box with title and columns."""
    n_cols = len(columns)
    height = title_height + n_cols * col_height + 0.08

    # Main box
    rect = FancyBboxPatch((x - width/2, y - height), width, height,
                          boxstyle="round,pad=0.02", 
                          facecolor='white', edgecolor=color, linewidth=2)
    ax.add_patch(rect)

    # Title bar
    title_rect = FancyBboxPatch((x - width/2, y - title_height), width, title_height,
                                boxstyle="round,pad=0.02", 
                                facecolor=color, edgecolor=color, linewidth=2)
    ax.add_patch(title_rect)
    ax.text(x, y - title_height/2, title, ha='center', va='center',
            fontsize=8.5, fontweight='bold', color='white')

    # Columns
    for i, col in enumerate(columns):
        cy = y - title_height - (i + 0.5) * col_height
        ax.text(x - width/2 + 0.08, cy, col, ha='left', va='center',
                fontsize=6.5, color='#333333', family='monospace')

    return (x, y, x, y - height, width, height)

def draw_relationship(ax, x1, y1, x2, y2, style='--'):
    """Draw a relationship line with crow's foot notation."""
    # Simple line
    ax.plot([x1, x2], [y1, y2], color='#666666', linewidth=1.0, linestyle=style, zorder=1)

def main():
    fig, ax = plt.subplots(1, 1, figsize=(32, 24), dpi=150)
    ax.set_xlim(0, 32)
    ax.set_ylim(0, 24)
    ax.axis('off')
    ax.set_facecolor('#F8F9FA')
    fig.patch.set_facecolor('#F8F9FA')

    # Title
    ax.text(16, 23.4, 'LUMI Database Entity-Relationship Diagram', 
            ha='center', va='center', fontsize=22, fontweight='bold', color='#2C3E50')
    ax.text(16, 22.9, 'PostgreSQL Schema v4  —  21 Tables + 1 Auth View', 
            ha='center', va='center', fontsize=12, color='#7F8C8D')

    # Legend
    legend_items = [
        ('Geographic Hierarchy', COLORS['geo']),
        ('Renewable Energy', COLORS['renewable']),
        ('Statistics & ML', COLORS['stats']),
        ('User Management', COLORS['user']),
        ('Auth / Cache', COLORS['auth']),
    ]
    for i, (label, color) in enumerate(legend_items):
        lx = 2 + i * 4.5
        ly = 22.3
        rect = mpatches.Rectangle((lx, ly - 0.12), 0.4, 0.24, facecolor=color, edgecolor='none')
        ax.add_patch(rect)
        ax.text(lx + 0.55, ly, label, ha='left', va='center', fontsize=9, color='#333')

    # ===== Geographic Hierarchy (left side) =====
    geo_x = 5.5

    t_regions = draw_table(ax, geo_x, 20.5, 'regions', [
        'region_id  PK',
        'name',
        'lat, lon',
    ], COLORS['geo'])

    t_provinces = draw_table(ax, geo_x, 16.8, 'provinces', [
        'province_id  PK',
        'region_id  FK',
        'name',
        'lat, lon',
    ], COLORS['geo'])

    t_municipalities = draw_table(ax, geo_x, 11.5, 'municipalities', [
        'municipality_id  PK',
        'province_id  FK',
        'name, lat, lon',
        'solar_suitability_score',
        'solar_classification',
        'wind_suitability_score',
        'wind_classification',
        'hydro_suitability_score',
        'hydro_classification',
        'geothermal_suitability_score',
        'geothermal_classification',
        'composite_suitability_score',
        'suitability_updated_at',
    ], COLORS['geo'], width=3.0)

    t_barangays = draw_table(ax, geo_x - 4.5, 7.0, 'barangays', [
        'barangay_id  PK',
        'municipality_id  FK',
        'name, lat, lon',
    ], COLORS['geo'])

    t_climate = draw_table(ax, geo_x + 4.5, 7.0, 'municipality_climate_monthly', [
        'municipality_id  FK',
        'year, month  PK',
        't2m, t2m_max, t2m_min',
        'rh2m, prectotcorr',
        'ws10m, allsky_sfc_sw_dwn',
        'cloud_amt, elevation',
        'source, created_at',
    ], COLORS['geo'], width=3.0)

    # ===== Renewable Energy (center-left) =====
    ren_x = 12.5

    t_hydro = draw_table(ax, ren_x, 20.0, 'hydropower_suitability', [
        'municipality_id  PK/FK',
        'province_id  FK',
        'mean_slope_deg',
        'hydraulic_head_m',
        'hydro_suitability_score',
        'estimated_potential_kw',
        'runoff_potential',
        'gravity_flow_potential',
        'slope_classification',
    ], COLORS['renewable'], width=2.8)

    t_geosuit = draw_table(ax, ren_x, 15.0, 'geothermal_suitability', [
        'municipality_id  PK/FK',
        'heat_flow_score',
        'fault_density',
        'fault_distance_km',
        'volcano_distance_km',
        'aquifer_score',
        'temperature_score',
        'geothermal_score',
        'classification',
    ], COLORS['renewable'], width=2.8)

    t_geoout = draw_table(ax, ren_x, 9.5, 'geothermal_output', [
        'municipality_id  PK/FK',
        'reservoir_temperature_c',
        'estimated_flow_rate_kg_s',
        'thermal_power_mw',
        'electric_power_mw',
        'annual_energy_gwh',
        'confidence_score',
    ], COLORS['renewable'], width=2.8)

    # ===== Stats & ML (center-right) =====
    stats_x = 19.0

    t_national = draw_table(ax, stats_x, 21.0, 'national_energy_annual', [
        'year  PK',
        'total_consumption_gwh',
        'total_peak_demand_mw',
        'luzon_generation_gwh',
        'renewable_generation_gwh',
        'total_installed_capacity_mw',
        'created_at, updated_at',
    ], COLORS['stats'], width=2.8)

    t_mlreg = draw_table(ax, stats_x, 16.5, 'ml_model_registry', [
        'model_id  PK',
        'model_name, version',
        'model_type',
        'target_variable',
        'train_date',
        'metrics (jsonb)',
        'is_active',
    ], COLORS['stats'], width=2.6)

    t_forecast = draw_table(ax, stats_x + 4.0, 16.5, 'forecast_cache', [
        'forecast_id  PK',
        'model_id  FK',
        'target_variable',
        'horizon_years',
        'forecast_year, month',
        'predicted_value',
        'lower_bound, upper_bound',
    ], COLORS['stats'], width=2.8)

    t_chart = draw_table(ax, stats_x + 4.0, 21.0, 'chart_ai_insights', [
        'id  PK',
        'chart_type',
        'chart_data_hash',
        'insight',
        'created_at',
    ], COLORS['cache'], width=2.4)

    # ===== User Management (bottom) =====
    user_y = 4.0
    user_x_start = 2.5
    user_spacing = 3.0

    t_auth = draw_table(ax, user_x_start, user_y + 1.0, 'auth.users', [
        'id  PK',
    ], COLORS['auth'], width=1.6)

    t_profiles = draw_table(ax, user_x_start + user_spacing, user_y, 'profiles', [
        'id  PK/FK',
        'full_name',
        'organization',
        'plan',
        'is_active',
        'created_at',
    ], COLORS['user'], width=2.0)

    t_roles = draw_table(ax, user_x_start + user_spacing*2, user_y, 'user_roles', [
        'user_id  PK/FK',
        'role (app_role)',
        'created_at',
    ], COLORS['user'], width=2.0)

    t_limits = draw_table(ax, user_x_start + user_spacing*3, user_y, 'user_usage_limits', [
        'user_id  PK/FK',
        'chat_messages_this_month',
        'simulations_this_month',
        'plan',
    ], COLORS['user'], width=2.2)

    t_chat_sess = draw_table(ax, user_x_start + user_spacing*4.2, user_y + 0.5, 'chat_sessions', [
        'id  PK',
        'user_id  FK',
        'title',
        'created_at',
    ], COLORS['user'], width=2.0)

    t_chat_msg = draw_table(ax, user_x_start + user_spacing*5.5, user_y + 0.5, 'chat_messages', [
        'id  PK',
        'session_id  FK',
        'role',
        'content',
        'retrieved_chunks',
    ], COLORS['user'], width=2.2)

    t_saved_loc = draw_table(ax, user_x_start + user_spacing*6.8, user_y, 'saved_locations', [
        'id  PK',
        'user_id  FK',
        'municipality_id  FK',
        'label',
        'created_at',
    ], COLORS['user'], width=2.2)

    t_saved_sim = draw_table(ax, user_x_start + user_spacing*8.1, user_y, 'saved_simulations', [
        'id  PK',
        'user_id  FK',
        'municipality_id  FK',
        'label',
        'inputs (jsonb)',
        'results (jsonb)',
    ], COLORS['user'], width=2.2)

    t_audit = draw_table(ax, user_x_start + user_spacing*9.4, user_y, 'admin_audit_log', [
        'id  PK',
        'admin_id  FK',
        'action',
        'target_user_id  FK',
        'details (jsonb)',
    ], COLORS['user'], width=2.3)

    # ===== Relationship lines =====
    # Geographic
    ax.annotate('', xy=(geo_x, t_provinces[1] + 0.2), xytext=(geo_x, t_regions[3]),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.2))
    ax.annotate('', xy=(geo_x, t_municipalities[1] + 0.2), xytext=(geo_x, t_provinces[3]),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.2))
    ax.annotate('', xy=(t_barangays[0] + t_barangays[4]/2, t_barangays[1] + 0.1), 
                xytext=(geo_x - t_municipalities[4]/2, t_municipalities[3] + 0.5),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.2, connectionstyle="arc3,rad=0.2"))
    ax.annotate('', xy=(t_climate[0] - t_climate[4]/2, t_climate[1] + 0.1), 
                xytext=(geo_x + t_municipalities[4]/2, t_municipalities[3] + 0.5),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.2, connectionstyle="arc3,rad=-0.2"))

    # Renewable -> municipalities
    ax.annotate('', xy=(ren_x - t_hydro[4]/2, t_hydro[3] + 0.2), 
                xytext=(geo_x + t_municipalities[4]/2, t_municipalities[3] + 0.2),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.2, connectionstyle="arc3,rad=0.15"))
    ax.annotate('', xy=(ren_x - t_geosuit[4]/2, t_geosuit[3] + 0.2), 
                xytext=(geo_x + t_municipalities[4]/2, t_municipalities[3] + 0.2),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.2, connectionstyle="arc3,rad=0.1"))
    ax.annotate('', xy=(ren_x - t_geoout[4]/2, t_geoout[3] + 0.2), 
                xytext=(geo_x + t_municipalities[4]/2, t_municipalities[3] + 0.2),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.2, connectionstyle="arc3,rad=0.05"))

    # ML -> forecast
    ax.annotate('', xy=(t_forecast[0] - t_forecast[4]/2, t_forecast[1] - 0.2), 
                xytext=(t_mlreg[0] + t_mlreg[4]/2, t_mlreg[1] - 0.2),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.2))

    # Auth -> user tables
    auth_top = (t_auth[0], t_auth[1])
    for t in [t_profiles, t_roles, t_limits]:
        ax.annotate('', xy=(t[0] - t[4]/2, (t[1] + t[3])/2), 
                    xytext=(auth_top[0] + t_auth[4]/2, auth_top[1] - 0.1),
                    arrowprops=dict(arrowstyle='->', color='#555', lw=1.0, connectionstyle="arc3,rad=0.1"))

    ax.annotate('', xy=(t_chat_sess[0] - t_chat_sess[4]/2, (t_chat_sess[1] + t_chat_sess[3])/2), 
                xytext=(auth_top[0] + t_auth[4]/2, auth_top[1] - 0.1),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.0, connectionstyle="arc3,rad=0.15"))
    ax.annotate('', xy=(t_saved_loc[0] - t_saved_loc[4]/2, (t_saved_loc[1] + t_saved_loc[3])/2), 
                xytext=(auth_top[0] + t_auth[4]/2, auth_top[1] - 0.1),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.0, connectionstyle="arc3,rad=0.2"))
    ax.annotate('', xy=(t_saved_sim[0] - t_saved_sim[4]/2, (t_saved_sim[1] + t_saved_sim[3])/2), 
                xytext=(auth_top[0] + t_auth[4]/2, auth_top[1] - 0.1),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.0, connectionstyle="arc3,rad=0.25"))
    ax.annotate('', xy=(t_audit[0] - t_audit[4]/2, (t_audit[1] + t_audit[3])/2), 
                xytext=(auth_top[0] + t_auth[4]/2, auth_top[1] - 0.1),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.0, connectionstyle="arc3,rad=0.3"))

    # Chat sessions -> messages
    ax.annotate('', xy=(t_chat_msg[0] - t_chat_msg[4]/2, (t_chat_msg[1] + t_chat_msg[3])/2), 
                xytext=(t_chat_sess[0] + t_chat_sess[4]/2, (t_chat_sess[1] + t_chat_sess[3])/2),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.0))

    # Saved items -> municipalities
    ax.annotate('', xy=(geo_x, t_municipalities[3]), 
                xytext=(t_saved_loc[0], t_saved_loc[1] + 0.2),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.0, connectionstyle="arc3,rad=0.3"))
    ax.annotate('', xy=(geo_x, t_municipalities[3]), 
                xytext=(t_saved_sim[0], t_saved_sim[1] + 0.2),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.0, connectionstyle="arc3,rad=-0.2"))

    # Domain labels
    ax.text(1.5, 21.5, 'Geographic\nHierarchy', ha='center', va='center', fontsize=10, 
            fontweight='bold', color=COLORS['geo'], style='italic')
    ax.text(10.0, 21.5, 'Renewable\nEnergy', ha='center', va='center', fontsize=10, 
            fontweight='bold', color=COLORS['renewable'], style='italic')
    ax.text(17.0, 23.0, 'Statistics &\nMachine Learning', ha='center', va='center', fontsize=10, 
            fontweight='bold', color=COLORS['stats'], style='italic')
    ax.text(1.5, 5.5, 'User\nManagement', ha='center', va='center', fontsize=10, 
            fontweight='bold', color=COLORS['user'], style='italic')

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=200, bbox_inches='tight', facecolor='#F8F9FA', edgecolor='none')
    print(f"ERD saved to {OUTPUT_PATH}")

if __name__ == '__main__':
    main()
