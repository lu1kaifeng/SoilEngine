import os

from flask import Flask, render_template
from config import DevelopmentConfig, ProductionConfig
from database import db
import sqlite3  as sql

from soil_report import extract_lon_lat, sentinel_2_img

app = Flask(__name__)

if os.environ.get('FLASK_ENV') == 'production':
    app.config.from_object(ProductionConfig)
else:
    app.config.from_object(DevelopmentConfig)

db.init_app(app)

@app.route('/report/<site_id>')
def report(site_id):
    with sql.connect(r'wcvs_soil_data_processed.sqlite') as conn:
        conn.row_factory = sql.Row
        sites = conn.execute('''select group_concat(site_id, ',')                             as site_id,
                                       group_concat(SUBSTR(lld, 1, INSTR(lld, '-') - 1), ',') as subdiv,-- Everything BEFORE the first space

                                       -- Everything AFTER the first space
                                       SUBSTR(lld, INSTR(lld, '-') + 1)                       AS lld_pfix
                                from sites
                                where not lld IS NULL and lld_pfix = ?
                                group by lld_pfix;''',(site_id,))
        site = sites.fetchone()
        site = dict(site)
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
        texture = conn.execute(f'select texture.depth_increment as depth_increment,avg(sand_percent) as sand, avg(silt_percent) as silt, avg(clay_percent) as clay,bd_notsplined as bd,texture_class from main.texture join bulk_density on texture.sample_point_id = bulk_density.sample_point_id where texture.sample_point_id in (select sample_point_id from sampling_points where  site_id in ({placeholders})) group by texture.depth_increment',site_id_list)
        texture = [dict(p) for p in texture]
        nutrient_organic = conn.execute(f'select nitrogen.depth_increment as depth_increment,avg(nitrogen.TN_percent) as TN_percent,avg(OC_percent) as OC_percent,avg(OM_percent) as OM_percent, avg(w.C_mgL_uncorrected) as C_mgL,avg(w.N_mgL_uncorrected) as N_mgL from nitrogen join main.carbon_and_OM caO on nitrogen.sample_point_id = caO.sample_point_id join main.weom w on caO.sample_point_id = w.sample_point_id  where nitrogen.sample_point_id in (select sample_point_id from sampling_points where  site_id in ({placeholders})) group by nitrogen.depth_increment',site_id_list)
        nutrient_organic = [dict(p) for p in nutrient_organic]
        ph_ec = conn.execute(f'select depth_increment,avg(ec_dSm) as ec_dSm, avg(ph) as pH from main.ph_ec where ph_ec.sample_point_id in (select sample_point_id from sampling_points where  site_id in ({placeholders})) group by depth_increment',site_id_list)
        ph_ec = [dict(p) for p in ph_ec]
        return render_template('report_template.html',minimap = minimap,texture=texture,nutrient_organic=nutrient_organic,ph_ec=ph_ec)

@app.route('/')
def hello_world():  # put application's code here
    with sql.connect(r'F:\soil_data_reporting\wcvs_soil_data_processed.sqlite') as conn:
        conn.row_factory = sql.Row
        sites = conn.execute('''select group_concat(site_id, ',')                             as site_id,
                                       group_concat(SUBSTR(lld, 1, INSTR(lld, '-') - 1), ',') as subdiv,-- Everything BEFORE the first space

                                       -- Everything AFTER the first space
                                       SUBSTR(lld, INSTR(lld, '-') + 1)                       AS lld_pfix
                                from sites
                                where not lld IS NULL
                                group by lld_pfix;''')
        return render_template('index.html',sites = [dict(s) for s in sites])
if __name__ == '__main__':
    app.run()
