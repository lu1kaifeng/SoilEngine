from sqlalchemy import Column, Integer, Float, String, Numeric, Date, DateTime, func
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass


class BulkDensity(Base):
    __tablename__ = 'bulk_density'
    __table_args__ = {'schema': 'new_schema'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    sample_number = Column(String, unique=True)
    sample_point_id = Column(String)
    depth_upper = Column(Integer)
    depth_lower = Column(Float)
    sample_wet_weight = Column(Float)
    tin_weight = Column(Float)
    tin_soil_wet_weight = Column(Float)
    tin_soil_dry_weight = Column(Float)
    core_diameter = Column(Float)
    bag_weight = Column(Float)
    coarse_fragment_weight = Column(Float)
    notes = Column(String)
    created = Column(DateTime, server_default=func.now())
    last_modified = Column(DateTime)


class Carbon(Base):
    __tablename__ = 'carbon'
    __table_args__ = {'schema': 'new_schema'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    sample_number = Column(String)
    sample_point_id = Column(String)
    depth_increment = Column(String)
    QA = Column(String)
    LECO_TC_sample_weight = Column(Float)
    LECO_TC_percent = Column(Float)
    LECO_TC_gkg = Column(Float)
    LECO_TC_analysis_date = Column(String)
    LECO_OC_sample_weight = Column(Float)
    LECO_OC_percent = Column(Float)
    LECO_OC_gkg = Column(Float)
    LECO_OC_analysis_date = Column(String)
    SOLI_sample_weight = Column(Numeric)
    SOLI_TC_percent = Column(Float)
    SOLI_IC_percent = Column(Float)
    SOLI_OC_percent = Column(Float)
    SOLI_analysis_date = Column(Date)
    notes = Column(String)
    created = Column(DateTime, server_default=func.now())
    last_modified = Column(DateTime)


class ChangeTrackingHistory(Base):
    __tablename__ = 'change_tracking_history'
    __table_args__ = {'schema': 'new_schema'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_action = Column(String)
    location = Column(String)
    timestamp = Column(DateTime)
    id_changed = Column(String)
    old_value = Column(String)
    new_value = Column(String)


class Nitrogen(Base):
    __tablename__ = 'nitrogen'
    __table_args__ = {'schema': 'new_schema'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    sample_number = Column(String)
    sample_point_id = Column(String)
    depth_increment = Column(String)
    QA = Column(String)
    TN_sample_weight = Column(Float)
    TN_percent = Column(Float)
    TN_analysis_date = Column(String)
    temp = Column(Integer)
    notes = Column(Integer)
    TN_redo = Column(Integer)
    created = Column(DateTime, server_default=func.now())
    last_modified = Column(DateTime)


class PhEc(Base):
    __tablename__ = 'ph_ec'
    __table_args__ = {'schema': 'new_schema'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    sample_point_id = Column(String)
    depth_increment = Column(String)
    sample_number = Column(String)
    pH = Column(Float)
    EC = Column(Float)
    EC_unit = Column(String)
    notes = Column(String)
    last_modified = Column(Date)


class SamplingPoint(Base):
    __tablename__ = 'sampling_points'
    __table_args__ = {'schema': 'new_schema'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    site_id = Column(Integer)
    transect = Column(Integer)
    lp = Column(Integer)
    lp_combined_3 = Column(String)
    em_v = Column(Float)
    em_h = Column(Float)
    lat = Column(Float)
    lon = Column(Float)
    sample_point_id = Column(String)
    photo = Column(String)
    notes = Column(String)
    geometry_x = Column(String)
    geometry_y = Column(String)
    waterfreq = Column(Float)


class Site(Base):
    __tablename__ = 'sites'
    __table_args__ = {'schema': 'new_schema'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    sampling_year = Column(Integer)
    sampling_date = Column(String)
    project = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    site_id = Column(Integer)
    soil_zone = Column(String)
    land_use = Column(String)
    management = Column(String)
    exclude = Column(String)
    wetland_class_summary = Column(String)
    wetland_class_actual = Column(String)
    wetland_class_pred = Column(String)
    aci = Column(String)
    pm = Column(String)
    ws_class_1 = Column(String)
    ws_class_2 = Column(String)
    texture = Column(String)
    texture_class = Column(String)
    nearest_city = Column(String)
    lld = Column(String)
    rm = Column(String)
    map_link = Column(String)
    collab = Column(String)
    notes = Column(String)
    google_earth_coords = Column(String)
    photo_site = Column(String)
    landowner_id = Column(Integer)
    geometry_x = Column(String)
    geometry_y = Column(String)
    area_sqm = Column(Float)


class SiteCsv(Base):
    __tablename__ = 'sites_csv'
    __table_args__ = {'schema': 'new_schema'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    sampling_y = Column(Integer)
    sampling_d = Column(String)
    project = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    soil_zone = Column(String)
    wetland_cl = Column(Integer)
    salinity_c = Column(Integer)
    pond_type = Column(String)
    tillage = Column(String)
    aci = Column(String)
    drained = Column(String)
    land_use = Column(String)
    landowner_ = Column(Integer)
    pm = Column(String)
    cultivated = Column(String)
    ws_class_1 = Column(String)
    ws_class_2 = Column(String)
    site_id = Column(Integer)
    lld = Column(String)
    rm = Column(String)
    nearest_ci = Column(String)
    google_ear = Column(String)
    map_link = Column(String)
    contact_ph = Column(String)
    contact_na = Column(String)
    contact_em = Column(String)
    collab = Column(String)
    notes = Column(String)
    photo_site = Column(String)


class Texture(Base):
    __tablename__ = 'texture'
    __table_args__ = {'schema': 'new_schema'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    sample_number = Column(String)
    sand_percent = Column(Float)
    silt_percent = Column(Float)
    clay_percent = Column(String)
    texture_class = Column(Numeric)
    notes = Column(String)
    created = Column(DateTime, server_default=func.now())
    last_modified = Column(DateTime)


class Weom(Base):
    __tablename__ = 'weom'
    __table_args__ = {'schema': 'new_schema'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    sample_point_id = Column(String)
    depth_increment = Column(String)
    sample_number = Column(String, unique=True)
    sample_wet_weight = Column(Float)
    tin_weight = Column(Float)
    tin_soil_wet_weight = Column(Float)
    tin_soil_dry_weight = Column(Float)
    sample_processed = Column(String)
    weom_analysis_date = Column(String)
    dilution = Column(Numeric)
    C_mgL_uncorrected = Column(Float)
    N_mgL_uncorrected = Column(Float)
    redo = Column(String)
    notes = Column(String)
    created = Column(DateTime, server_default=func.now())
    last_modified = Column(DateTime)