import sqlite3  as sql
import planetary_computer
import pystac_client
import rioxarray
from matplotlib import pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
from shapely.geometry import Polygon
import stackstac


def sentinel_2_img(bbox):
    # 3. Query Microsoft Planetary Computer STAC Catalog
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )

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

    # 4. Plot image with spatial extent
    fig, ax = plt.subplots(figsize=(9, 9))
    ax.imshow(rgb_scaled, extent=[x_min, x_max, y_min, y_max])
    ax.axis("off")

    # 5. Add Scale Bar (1 coordinate unit = 1 meter in EPSG:3857)
    scalebar = ScaleBar(
        dx=1.0,
        units="m",
        location="lower right",
        box_alpha=0.6,
        color="black",
        font_properties={"weight": "bold"},
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

    add_north_arrow(ax)

    plt.title(f"Sentinel-2 Image ({latest_scene.datetime.strftime('%Y-%m-%d')})")
    plt.savefig("sentinel2_map.png", bbox_inches="tight", dpi=300)
    plt.show()

def extract_lon_lat(point):
    return point['lon'], point['lat']

with sql.connect(r'F:\soil_data_reporting\wcvs_soil_data_processed.sqlite') as conn:
    conn.row_factory = sql.Row
    sites = conn.execute('select * from sites')
    all_points = []
    for site in sites:
        site = dict(site)
        site_id = site['site_id']
        points = conn.execute('select * from main.sampling_points where site_id = ?', (site_id,))
        points = [dict(p) for p in points]
        lon_lat = [extract_lon_lat(p) for p in points]
        bounding_box = Polygon(lon_lat)
        sentinel_2_img(list(bounding_box.bounds))
        pass
