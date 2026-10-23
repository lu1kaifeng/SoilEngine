from datetime import datetime
import os
import re

from flask import Flask, render_template
from config import DevelopmentConfig, ProductionConfig
from database import db
import sqlite3  as sql
from model.density_map import if_compacted as if_compacted_func
from soil_report import extract_lon_lat, sentinel_2_img
from model.salinity import salinity, get_salinity
app = Flask(__name__)

if os.environ.get('FLASK_ENV') == 'production':
    app.config.from_object(ProductionConfig)
else:
    app.config.from_object(DevelopmentConfig)

db.init_app(app)

brand_blue = "#0B6A41"  # Traditional USask Green hex fallback
brand_orange = "#FDD62D"  # Traditional USask Gold hex fallback

@app.context_processor
def inject_now():
    # Makes 'now' variable available in every Jinja template
    return {'now': datetime.utcnow()}

@app.template_global()
def if_compacted(texture,db_val):
    return if_compacted_func(texture, db_val)

@app.template_global()
def salinity_level(sal_val: float):
    if sal_val is None:
        return ""
    sal_txt1, sal_txt2,t3 = get_salinity(sal_val)
    return sal_txt2,t3

@app.template_global()
def salinity_color(sal_val: float):
    if sal_val is None:
        return "auto"
    sal_val = max(0.0, min(16.0, float(sal_val))) / 16.
    return interpolate_rgb(brand_orange,brand_blue,sal_val)

@app.template_global()
def salinity_text_color(sal_val: float):
    if sal_val is None:
        return False
    sal_val = max(0.0, min(16.0, float(sal_val))) / 16.
    return sal_val > 0.5

def interpolate_rgb(color1: str, color2: str, value: float) -> str:
    # 1. Clamp value strictly between 0.0 and 1.0
    t = max(0.0, min(1.0, float(value)))

    # Helper function to convert #ffffff or ffffff to (R, G, B) tuple
    def parse_hex(hex_str: str):
        cleaned = hex_str.lstrip('#')
        # Matches pairs of hex characters
        hex_pairs = re.findall(r'.{1,2}', cleaned)
        return [int(pair, 16) for pair in hex_pairs]

    r1, g1, b1 = parse_hex(color1)
    r2, g2, b2 = parse_hex(color2)

    # 2. Linear Interpolation formula: start + (end - start) * t
    r = round(r1 + (r2 - r1) * t)
    g = round(g1 + (g2 - g1) * t)
    b = round(b1 + (b2 - b1) * t)

    return f"rgb({r}, {g}, {b})"

@app.template_global()
def if_white_text(avg: float,val: float)-> bool:
    if avg is None or val is None:
        return False
    if val > avg:
        return True
    return False
    pass
@app.template_global()
def val_to_color(avg: float, std: float, val: float) -> str:
    # Python alternative to fetching CSS variables (manually provided here)
    # Replaces window.getComputedStyle(document.documentElement)...
    if avg is None or val is None or std is None:
        return False

    max_absolute_z = 3.0

    # Avoid DivisionByZero if standard deviation is 0
    if std == 0:
        z = 0.0
    else:
        z = (val - avg) / std

    # Clamp Z-score between -3.0 and +3.0
    z = max(-max_absolute_z, min(max_absolute_z, z))

    # Normalize the Z-score cleanly to a 0.0 - 1.0 range
    normalized = (z + max_absolute_z) / (2.0 * max_absolute_z)

    # Return the final rgb string output
    return interpolate_rgb(brand_orange, brand_blue, normalized)

def _find_global_avg(conn: sql.Connection, pm, soil_zone):
    sites = conn.execute('''select group_concat(site_id, ',')                             as site_id,

                                       pm,soil_zone
                                from sites
                                where not lld IS NULL and pm = ? and soil_zone = ?
                                group by pm,soil_zone;''',(pm,soil_zone))
    site = sites.fetchone()
    site = dict(site)
    site_id = site['site_id']
    site_id_list = [s.strip() for s in site_id.split(',')]
    placeholders = ', '.join(['?'] * len(site_id_list))
    nutrient_organic = conn.execute(
        f'select nitrogen.depth_increment as depth_increment,'
        f'avg(nitrogen.TN_percent) as TN_percent_avg'
        f',sqrt(avg(nitrogen.TN_percent*nitrogen.TN_percent) - avg(nitrogen.TN_percent)*avg(nitrogen.TN_percent)) as TN_percent_std'
        f',avg(OC_percent) as OC_percent_avg'
        f',sqrt(avg(OC_percent*OC_percent) - avg(OC_percent)*avg(OC_percent)) as OC_percent_std'
        f',avg(OM_percent) as OM_percent_avg'
        f',sqrt(avg(OM_percent*OM_percent) - avg(OM_percent)*avg(OM_percent)) as OM_percent_std'
        f', avg(w.C_mgL_uncorrected) as C_mgL,'
        f'avg(w.N_mgL_uncorrected) as N_mgL from nitrogen join main.carbon_and_OM caO on nitrogen.sample_point_id = caO.sample_point_id join main.weom w on caO.sample_point_id = w.sample_point_id  where nitrogen.sample_point_id in (select sample_point_id from sampling_points where  site_id in ({placeholders})) group by nitrogen.depth_increment',
        site_id_list)
    nutrient_organic = {p['depth_increment']:dict(p) for p in nutrient_organic}
    return nutrient_organic

@app.route('/report/<site_id>')
def report(site_id):
    with sql.connect(r'wcvs_soil_data_processed.sqlite') as conn:
        conn.row_factory = sql.Row
        sites = conn.execute('''select group_concat(site_id, ',')                             as site_id,
                                       group_concat(SUBSTR(lld, 1, INSTR(lld, '-') - 1), ',') as subdiv,-- Everything BEFORE the first space

                                       -- Everything AFTER the first space
                                       SUBSTR(lld, INSTR(lld, '-') + 1)                       AS lld_pfix,lld,min(pm) as pm,min(soil_zone) as soil_zone,rm,SUM(area_sqm) as area_sqm,sampling_date
                                from sites
                                where not lld IS NULL and lld = ?
                                group by lld;''',(site_id,))
        site = sites.fetchone()
        site = dict(site)
        pm = site['pm']
        soil_zone = site['soil_zone']
        site_id = site['site_id']
        site_id_list = [s.strip() for s in site_id.split(',')]

        # Generate a string of placeholders matching the number of items: '?, ?, ?'
        placeholders = ', '.join(['?'] * len(site_id_list))
        query = f'SELECT * FROM main.sampling_points WHERE site_id IN ({placeholders})'

        # Pass the list directly as the parameter sequence
        points = conn.execute(query, site_id_list)
        points = [dict(p) for p in points]
        lon_lat = [extract_lon_lat(p) for p in points]
        lon_lat = list(filter(lambda ll: False if ll[0] is None or ll[1] is None else True, lon_lat))
        if len(lon_lat) == 0:
            return "No data for this land.", 204
        minimap = sentinel_2_img(lon_lat)

        #bd = conn.execute(f'select depth_increment,avg(bd_notsplined) as bd from main.bulk_density where bulk_density.sample_point_id in (select sample_point_id from sampling_points where  site_id in ({placeholders})) group by depth_increment',site_id_list)
        #bd = [dict(p) for p in bd]
        texture = conn.execute(f'select texture.depth_increment as depth_increment,avg(sand_percent) as sand, avg(silt_percent) as silt, avg(clay_percent) as clay,bd_notsplined as bd,texture_class from main.texture join bulk_density on texture.sample_point_id = bulk_density.sample_point_id and texture.depth_increment = bulk_density.depth_increment where texture.sample_point_id in (select sample_point_id from sampling_points where  site_id in ({placeholders})) group by texture.depth_increment',site_id_list)
        texture = [dict(p) for p in texture]
        nutrient_organic = conn.execute(f'select nitrogen.depth_increment as depth_increment,avg(nitrogen.TN_percent) as TN_percent,avg(OC_percent) as OC_percent,avg(OM_percent) as OM_percent, avg(w.C_mgL_uncorrected) as C_mgL,avg(w.N_mgL_uncorrected) as N_mgL from nitrogen join main.carbon_and_OM caO on nitrogen.sample_point_id = caO.sample_point_id and caO.sample_number = nitrogen.sample_number join main.weom w on caO.sample_point_id = w.sample_point_id and w.sample_number = caO.sample_number where nitrogen.sample_point_id in (select sample_point_id from sampling_points where  site_id in ({placeholders})) group by nitrogen.depth_increment',site_id_list)
        nutrient_organic = [dict(p) for p in nutrient_organic]
        ph_ec = conn.execute(f'select depth_increment,avg(ec_dSm) as ec_dSm, avg(ph) as pH from main.ph_ec where ph_ec.sample_point_id in (select sample_point_id from sampling_points where  site_id in ({placeholders})) group by depth_increment',site_id_list)
        ph_ec = [dict(p) for p in ph_ec]
        return render_template('report_template.html',site=site,minimap = minimap,texture=texture,nutrient_organic=nutrient_organic,ph_ec=ph_ec,global_avg = _find_global_avg(conn,pm,soil_zone))

@app.route('/')
def hello_world():  # put application's code here
    with sql.connect(r'wcvs_soil_data_processed.sqlite') as conn:
        conn.row_factory = sql.Row
        sites = conn.execute('''select group_concat(site_id, ',')                             as site_id,
                                       group_concat(SUBSTR(lld, 1, INSTR(lld, '-') - 1), ',') as subdiv,-- Everything BEFORE the first space

                                       -- Everything AFTER the first space
                                       SUBSTR(lld, INSTR(lld, '-') + 1)                       AS lld_pfix,lld
                                from sites
                                where not lld IS NULL
                                group by lld;''')
        return render_template('index.html',sites = [dict(s) for s in sites])
if __name__ == '__main__':
    app.run()
