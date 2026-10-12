import io
import sqlite3  as sql
import planetary_computer
import pystac_client
import rioxarray
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
from shapely.geometry import MultiPoint
import stackstac
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from jinja2 import Environment, FileSystemLoader

def sentinel_2_img(points):
    # 3. Query Microsoft Planetary Computer STAC Catalog
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )

    all_coords = points
    padded_poly = MultiPoint(all_coords).convex_hull.buffer(0.005)
    bbox = list(padded_poly.bounds)

    search = catalog.search(
        collections=["sentinel-2-l2a"],
        bbox=bbox,
        datetime="2024-05-01/2024-07-01",  # Date range
        query={"eo:cloud_cover": {"lt": 10}},  # Cloud cover threshold (< 10%)
    )

    items = search.item_collection()
    print(f"Found {len(items)} matching Sentinel-2 scenes.")

    # 4. Load & Crop the imagery for the bounding box
    # Fetching RGB bands: Red (B04), Green (B03), Blue (B02)
    latest_scene = items[0]

    data = stackstac.stack(
        latest_scene,
        assets=["B04", "B03", "B02"],
        bounds_latlon=bbox,  # Crop directly to bounding box
        epsg=3857,  # Project to Web Mercator
    )

    # 5. Process reflectance values to 0-1 range for RGB rendering
    rgb_data = data.squeeze().transpose("y", "x", "band").compute()
    rgb_scaled = (rgb_data / 3000.0).clip(0, 1)

    # Extract spatial extent in meters
    x_min, x_max = float(data.x.min()), float(data.x.max())
    y_min, y_max = float(data.y.min()), float(data.y.max())

    # 4. Set fixed figure dimensions
    DPI = 100
    FIG_WIDTH, FIG_HEIGHT = 200 / DPI, 180 / DPI  # Fixed output size


    fig = plt.figure(figsize=(FIG_WIDTH,FIG_HEIGHT), dpi=DPI,facecolor="none")
    proj = ccrs.epsg(3857)
    ax = fig.add_axes([0, 0, 1, 1], projection=proj, facecolor="none")

    # 5. Display Image (fixed canvas)
    # Using 'aspect="auto"' as requested before to fill the fixed frame.
    # We map the data using the computed 'extent'.
    ax.imshow(rgb_scaled, extent=[x_min, x_max, y_min, y_max],
              origin='upper',  transform=proj)

    ax.axis("off")  # Turn off default lat/lon grid for a clean map

    # 5. Add Scale Bar (1 coordinate unit = 1 meter in EPSG:3857)
    scalebar = ScaleBar(
        dx=1.0,
        units="m",
        location="lower right",
        box_alpha=0.6,
        color="black",
        font_properties={"weight": "bold","size":9},
    )
    ax.add_artist(scalebar)
    # 6. Add North Arrow (Compass)
    def add_north_arrow(ax, x=0.08, y=0.92, arrow_length=0.06):
        ax.annotate(
            "N",
            xy=(x, y),
            xytext=(x, y - arrow_length),
            xycoords="axes fraction",
            textcoords="axes fraction",
            ha="center",
            va="top",
            fontsize=13,
            fontweight="bold",
            arrowprops=dict(facecolor="black", width=3, headwidth=9, shrink=0.05),
            bbox=dict(boxstyle="circle,pad=0.3", fc="white", ec="none", alpha=0.6),
        )

    #add_north_arrow(ax)
    input_projection = ccrs.PlateCarree()
    if points is not None:
        for lon,lat in points:
            # Use a specific marker style (e.g., a "marker" with a border)
            ax.plot(lon, lat, marker='o', markersize=8,
                    markerfacecolor='red', markeredgecolor='white', markeredgewidth=2,
                    transform=input_projection,  # Crucial
                    zorder=20)


    #plt.title(f"Sentinel-2 Image ({latest_scene.datetime.strftime('%Y-%m-%d')})")
    buf = io.StringIO()
    plt.savefig(buf, format="svg" , bbox_inches=None, pad_inches=0, transparent=True,facecolor="none",edgecolor="none")
    svg_string = buf.getvalue()
    plt.close(fig)
    return svg_string

def extract_lon_lat(point):
    return point['lon'], point['lat']


if __name__ == '__main__':
    with sql.connect(r'F:\soil_data_reporting\wcvs_soil_data_processed.sqlite') as conn:
        conn.row_factory = sql.Row
        sites = conn.execute('''select group_concat(site_id,',') as site_id,group_concat(SUBSTR(lld, 1, INSTR(lld, '-') - 1),',') as subdiv,-- Everything BEFORE the first space
    
        -- Everything AFTER the first space
        SUBSTR(lld, INSTR(lld, '-') + 1)    AS lld_pfix
    from sites where not lld IS NULL
    group by lld_pfix ;''')
        # 1. Point Jinja to the directory where your templates live
        file_loader = FileSystemLoader('templates')

        # 2. Initialize the environment
        env = Environment(loader=file_loader)

        # 3. Load the specific template file
        template = env.get_template('report_template.html')
        all_points = []
        for site in sites:
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
                continue
            minimap = sentinel_2_img(lon_lat)
            with open(site['site_id']+'.html','w', encoding='utf-8') as f:
                f.write(template.render(minimap = minimap))
            pass
