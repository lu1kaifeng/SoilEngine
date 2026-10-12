ATTACH DATABASE 'F:\soil_data_reporting\soil_engine.sqlite' as new_schema;
-- 1. BULK_DENSITY
CREATE TABLE new_schema.bulk_density (
    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
    sample_number          TEXT UNIQUE,
    sample_point_id        TEXT,
    depth_upper            INTEGER,
    depth_lower            REAL,
    sample_wet_weight      REAL,
    tin_weight             REAL,
    tin_soil_wet_weight    REAL,
    tin_soil_dry_weight    REAL,
    core_diameter          REAL,
    bag_weight             REAL,
    coarse_fragment_weight REAL,
    notes                  TEXT,
    created                DATETIME DEFAULT (DATETIME('NOW')),
    last_modified          DATETIME
);

INSERT INTO new_schema.bulk_density (
    sample_number, sample_point_id, depth_upper, depth_lower,
    sample_wet_weight, tin_weight, tin_soil_wet_weight, tin_soil_dry_weight,
    core_diameter, bag_weight, coarse_fragment_weight, notes, created, last_modified
)
SELECT
    sample_number, sample_point_id, depth_upper, depth_lower,
    sample_wet_weight, tin_weight, tin_soil_wet_weight, tin_soil_dry_weight,
    core_diameter, bag_weight, coarse_fragment_weight, notes, created, last_modified
FROM main.bulk_density;


-- 2. CARBON
CREATE TABLE new_schema.carbon (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    sample_number         TEXT,
    sample_point_id       TEXT,
    depth_increment       TEXT,
    QA                    TEXT,
    LECO_TC_sample_weight REAL,
    LECO_TC_percent       REAL,
    LECO_TC_gkg           REAL,
    LECO_TC_analysis_date TEXT,
    LECO_OC_sample_weight REAL,
    LECO_OC_percent       REAL,
    LECO_OC_gkg           REAL,
    LECO_OC_analysis_date TEXT,
    SOLI_sample_weight    NUMERIC,
    SOLI_TC_percent       REAL,
    SOLI_IC_percent       REAL,
    SOLI_OC_percent       REAL,
    SOLI_analysis_date    DATE,
    notes                 TEXT,
    created               DATETIME DEFAULT (DATETIME('NOW', 'localtime')),
    last_modified         DATETIME
);

INSERT INTO new_schema.carbon (
    sample_number, sample_point_id, depth_increment, QA,
    LECO_TC_sample_weight, LECO_TC_percent, LECO_TC_gkg, LECO_TC_analysis_date,
    LECO_OC_sample_weight, LECO_OC_percent, LECO_OC_gkg, LECO_OC_analysis_date,
    SOLI_sample_weight, SOLI_TC_percent, SOLI_IC_percent, SOLI_OC_percent,
    SOLI_analysis_date, notes, created, last_modified
)
SELECT
    sample_number, sample_point_id, depth_increment, QA,
    LECO_TC_sample_weight, LECO_TC_percent, LECO_TC_gkg, LECO_TC_analysis_date,
    LECO_OC_sample_weight, LECO_OC_percent, LECO_OC_gkg, LECO_OC_analysis_date,
    SOLI_sample_weight, SOLI_TC_percent, SOLI_IC_percent, SOLI_OC_percent,
    SOLI_analysis_date, notes, created, last_modified
FROM main.carbon;


-- 3. CHANGE_TRACKING_HISTORY
CREATE TABLE new_schema.change_tracking_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_action TEXT,
    location    TEXT,
    timestamp   DATETIME,
    id_changed  TEXT,
    old_value   TEXT,
    new_value   TEXT
);

INSERT INTO new_schema.change_tracking_history (
    user_action, location, timestamp, id_changed, old_value, new_value
)
SELECT
    user_action, location, timestamp, id_changed, old_value, new_value
FROM main.change_tracking_history;


-- 4. NITROGEN
CREATE TABLE new_schema.nitrogen (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    sample_number    TEXT,
    sample_point_id  TEXT,
    depth_increment  TEXT,
    QA               TEXT,
    TN_sample_weight REAL,
    TN_percent       REAL,
    TN_analysis_date TEXT,
    temp             INTEGER,
    notes            INTEGER,
    TN_redo          INTEGER,
    created          DATETIME DEFAULT (DATETIME('NOW')),
    last_modified    DATETIME
);

INSERT INTO new_schema.nitrogen (
    sample_number, sample_point_id, depth_increment, QA,
    TN_sample_weight, TN_percent, TN_analysis_date, temp, notes, TN_redo, created, last_modified
)
SELECT
    sample_number, sample_point_id, depth_increment, QA,
    TN_sample_weight, TN_percent, TN_analysis_date, temp, notes, TN_redo, created, last_modified
FROM main.nitrogen;


-- 5. PH_EC
CREATE TABLE new_schema.ph_ec (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sample_point_id TEXT,
    depth_increment TEXT,
    sample_number   TEXT,
    pH              REAL,
    EC              REAL,
    EC_unit         TEXT,
    notes           TEXT,
    last_modified   DATE
);

INSERT INTO new_schema.ph_ec (
    sample_point_id, depth_increment, sample_number, pH, EC, EC_unit, notes, last_modified
)
SELECT
    sample_point_id, depth_increment, sample_number, pH, EC, EC_unit, notes, last_modified
FROM main.ph_ec;


-- 6. SAMPLING_POINTS
CREATE TABLE new_schema.sampling_points (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    site_id         INTEGER,
    transect        INTEGER,
    lp              INTEGER,
    lp_combined_3   TEXT,
    em_v            REAL,
    em_h            REAL,
    lat             REAL,
    lon             REAL,
    sample_point_id TEXT,
    photo           TEXT,
    notes           TEXT,
    geometry_x      TEXT,
    geometry_y      TEXT,
    waterfreq       REAL
);

INSERT INTO new_schema.sampling_points (
    site_id, transect, lp, lp_combined_3, em_v, em_h, lat, lon,
    sample_point_id, photo, notes, geometry_x, geometry_y, waterfreq
)
SELECT
    site_id, transect, lp, lp_combined_3, em_v, em_h, lat, lon,
    sample_point_id, photo, notes, geometry_x, geometry_y, waterfreq
FROM main.sampling_points;


-- 7. SITES
CREATE TABLE new_schema.sites (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    sampling_year         INTEGER,
    sampling_date         TEXT,
    project               TEXT,
    lat                   REAL,
    lon                   REAL,
    site_id               INTEGER,
    soil_zone             TEXT,
    land_use              TEXT,
    management            TEXT,
    exclude               TEXT,
    wetland_class_summary TEXT,
    wetland_class_actual  TEXT,
    wetland_class_pred    TEXT,
    aci                   TEXT,
    pm                    TEXT,
    ws_class_1            TEXT,
    ws_class_2            TEXT,
    texture               TEXT,
    texture_class         TEXT,
    nearest_city          TEXT,
    lld                   TEXT,
    rm                    TEXT,
    map_link              TEXT,
    collab                TEXT,
    notes                 TEXT,
    google_earth_coords   TEXT,
    photo_site            TEXT,
    landowner_id          INTEGER,
    geometry_x            TEXT,
    geometry_y            TEXT,
    area_sqm              REAL
);

INSERT INTO new_schema.sites (
    sampling_year, sampling_date, project, lat, lon, site_id, soil_zone, land_use,
    management, exclude, wetland_class_summary, wetland_class_actual, wetland_class_pred,
    aci, pm, ws_class_1, ws_class_2, texture, texture_class, nearest_city, lld, rm,
    map_link, collab, notes, google_earth_coords, photo_site, landowner_id,
    geometry_x, geometry_y, area_sqm
)
SELECT
    sampling_year, sampling_date, project, lat, lon, site_id, soil_zone, land_use,
    management, exclude, wetland_class_summary, wetland_class_actual, wetland_class_pred,
    aci, pm, ws_class_1, ws_class_2, texture, texture_class, nearest_city, lld, rm,
    map_link, collab, notes, google_earth_coords, photo_site, landowner_id,
    geometry_x, geometry_y, area_sqm
FROM main.sites;


-- 8. SITES_CSV
CREATE TABLE new_schema.sites_csv (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    sampling_y  INTEGER,
    sampling_d  TEXT,
    project     TEXT,
    lat         REAL,
    lon         REAL,
    soil_zone   TEXT,
    wetland_cl  INTEGER,
    salinity_c  INTEGER,
    pond_type   TEXT,
    tillage     TEXT,
    aci         TEXT,
    drained     TEXT,
    land_use    TEXT,
    landowner_  INTEGER,
    pm          TEXT,
    cultivated  TEXT,
    ws_class_1  TEXT,
    ws_class_2  TEXT,
    site_id     INTEGER,
    lld         TEXT,
    rm          TEXT,
    nearest_ci  TEXT,
    google_ear  TEXT,
    map_link    TEXT,
    contact_ph  TEXT,
    contact_na  TEXT,
    contact_em  TEXT,
    collab      TEXT,
    notes       TEXT,
    photo_site  TEXT
);

INSERT INTO new_schema.sites_csv (
    sampling_y, sampling_d, project, lat, lon, soil_zone, wetland_cl, salinity_c,
    pond_type, tillage, aci, drained, land_use, landowner_, pm, cultivated,
    ws_class_1, ws_class_2, site_id, lld, rm, nearest_ci, google_ear, map_link,
    contact_ph, contact_na, contact_em, collab, notes, photo_site
)
SELECT
    sampling_y, sampling_d, project, lat, lon, soil_zone, wetland_cl, salinity_c,
    pond_type, tillage, aci, drained, land_use, landowner_, pm, cultivated,
    ws_class_1, ws_class_2, site_id, lld, rm, nearest_ci, google_ear, map_link,
    contact_ph, contact_na, contact_em, collab, notes, photo_site
FROM main.sites_csv;


-- 9. TEXTURE
CREATE TABLE new_schema.texture (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    sample_number TEXT,
    sand_percent  REAL,
    silt_percent  REAL,
    clay_percent  TEXT,
    texture_class NUMERIC,
    notes         TEXT,
    created       DATETIME DEFAULT (DATETIME('NOW', 'localtime')),
    last_modified DATETIME
);

INSERT INTO new_schema.texture (
    sample_number, sand_percent, silt_percent, clay_percent, texture_class, notes, created, last_modified
)
SELECT
    sample_number, sand_percent, silt_percent, clay_percent, texture_class, notes, created, last_modified
FROM main.texture;


-- 10. WEOM
CREATE TABLE new_schema.weom (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    sample_point_id     TEXT,
    depth_increment     TEXT,
    sample_number       TEXT UNIQUE,
    sample_wet_weight   REAL,
    tin_weight          REAL,
    tin_soil_wet_weight REAL,
    tin_soil_dry_weight REAL,
    sample_processed    TEXT,
    weom_analysis_date  TEXT,
    dilution            NUMERIC,
    C_mgL_uncorrected   REAL,
    N_mgL_uncorrected   REAL,
    redo                TEXT,
    notes               TEXT,
    created             DATETIME DEFAULT (DATETIME('NOW')),
    last_modified       DATETIME
);

INSERT INTO new_schema.weom (
    sample_point_id, depth_increment, sample_number, sample_wet_weight, tin_weight,
    tin_soil_wet_weight, tin_soil_dry_weight, sample_processed, weom_analysis_date,
    dilution, C_mgL_uncorrected, N_mgL_uncorrected, redo, notes, created, last_modified
)
SELECT
    sample_point_id, depth_increment, sample_number, sample_wet_weight, tin_weight,
    tin_soil_wet_weight, tin_soil_dry_weight, sample_processed, weom_analysis_date,
    dilution, C_mgL_uncorrected, N_mgL_uncorrected, redo, notes, created, last_modified
FROM main.weom;