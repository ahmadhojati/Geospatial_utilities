#!/usr/bin/env python
# coding: utf-8



import rasterio
from rasterio.warp import transform, calculate_default_transform
from rasterio.enums import Resampling
import numpy as np
import pyproj

def resample_and_extract_value(tiff_file, coordinate, old_resolution_meters, new_resolution_meters):
    """
    Resamples a GeoTIFF image to a new resolution and extracts the pixel value at a specific coordinate.

    Parameters:
    - tiff_file (str): Path to the input GeoTIFF file.
    - coordinate (tuple): A tuple containing latitude and longitude coordinates in decimal degrees (lat, lon).
    - old_resolution_meters (float): The original pixel resolution in meters.
    - new_resolution_meters (float): The desired new pixel resolution in meters.

    Returns:
    - value (float or None): The extracted pixel value at the specified coordinate in the resampled image.
      Returns None if the coordinate is out of bounds or if the extracted value is NaN.
    """
    values = []

    with rasterio.open(tiff_file) as dataset:
        # Define the source and target coordinate reference systems (CRS)
        src_crs = dataset.crs
        utm_zone = get_utm_zone(coordinate[1])
        hemisphere = 'N' if coordinate[0] >= 0 else 'S'
        epsg_code = get_epsg_code(utm_zone, hemisphere)
        dst_crs = pyproj.CRS.from_epsg(epsg_code)  # Replace with the UTM zone appropriate for your location

        # Perform the coordinate transformation
        lon, lat = coordinate[1], coordinate[0]
        transformer = pyproj.Transformer.from_crs(src_crs, dst_crs, always_xy=True)
        easting, northing = transformer.transform(lon, lat)

        # Calculate the resampling scale factors in pixels
        scale_factor_x = new_resolution_meters / old_resolution_meters
        scale_factor_y = new_resolution_meters / old_resolution_meters

        # Calculate the destination bounds and dimensions
        dst_width = int(dataset.width * scale_factor_x)
        dst_height = int(dataset.height * scale_factor_y)

        dst_transform, dst_width, dst_height = calculate_default_transform(
            src_crs, dst_crs, dataset.width, dataset.height, *dataset.bounds,
            dst_width=dst_width, dst_height=dst_height
        )

        # Read the entire dataset resampled to the new resolution
        data = dataset.read(
            1,
            window=((0, dst_height), (0, dst_width)),
            out_shape=(1, dst_height, dst_width),
            resampling=Resampling.bilinear,
        )

        # Calculate the pixel coordinates within the resampled data
        pixel_col, pixel_row = ~dst_transform * (easting, northing)
        try:
            # Extract the value from the resampled data
            extracted_value = data[int(pixel_row), int(pixel_col)]

            if np.isnan(extracted_value):
                values.append(None)  # Append None for NaN values
            else:
                values.append(extracted_value)
        except (IndexError, ValueError):  # Handle errors and out-of-bounds coordinates
            values.append(None)  # Append None for missing values

    return values[0]


def get_utm_zone(longitude):
    """
    Determines the UTM (Universal Transverse Mercator) zone number based on a given longitude.

    Parameters:
    - longitude (float): The longitude in decimal degrees.

    Returns:
    - zone_number (int): The UTM zone number corresponding to the provided longitude.
    """
    zone_number = int((longitude + 180) / 6) + 1
    if zone_number > 60:
        zone_number = 1
    return zone_number

def get_epsg_code(utm_zone, hemisphere):
    """
    Computes the EPSG (European Petroleum Survey Group) code for a specific UTM zone and hemisphere.

    Parameters:
    - utm_zone (int): The UTM zone number.
    - hemisphere (str): Hemisphere identifier ('N' for Northern or 'S' for Southern).

    Returns:
    - epsg_code (int): The EPSG code representing the UTM zone and hemisphere combination.
    """
    if hemisphere == 'N':
        epsg_code = 32600 + utm_zone
    elif hemisphere == 'S':
        epsg_code = 32700 + utm_zone
    return epsg_code

def extract_values_at_coordinates(tiff_file, coordinate):
    """
    Extracts pixel values at specified coordinates from a GeoTIFF file.

    Parameters:
    - tiff_file (str): Path to the input GeoTIFF file.
    - coordinate (tuple): A tuple containing latitude and longitude coordinates in decimal degrees (lat, lon).

    Returns:
    - values (list): A list of extracted pixel values at the specified coordinate.
      The list may contain one or more values, or None if the coordinate is out of bounds or if values are missing.
    """
    import rasterio
    
    values = []
    with rasterio.open(tiff_file) as dataset:
        bounds = dataset.bounds  # Get the extent (bounding box) of the raster
        if (
            bounds.left <= coordinate[1] <= bounds.right and
            bounds.bottom <= coordinate[0] <= bounds.top
        ):
            row, col = dataset.index(coordinate[1], coordinate[0])
            try:
                value = dataset.read(1, window=((row, row + 1), (col, col + 1)))[0, 0]
                values.append(value)
            except IndexError:  # Skip if coordinate is out of bounds
                values.append(None)  # Append None for missing values
        else:
            values.append(None)  # Append None if coordinate is out of bounds
    return values

def lee_filter(window_size, tiff_file, coordinate):
    """
    Applies the Lee filter to a specific window in a GeoTIFF file and extracts the filtered value at a given coordinate.

    The Lee filter is a speckle reduction filter used in remote sensing to enhance image quality.

    Parameters:
    - window_size (int): The size of the square window used for filtering. A larger window size may provide better filtering, but it can be computationally intensive.
    - tiff_file (str): Path to the input GeoTIFF file.
    - coordinate (tuple): A tuple containing latitude and longitude coordinates in decimal degrees (lat, lon).

    Returns:
    - filtered_value (float or None): The filtered value at the specified coordinate after applying the Lee filter. Returns None if the coordinate is out of bounds.
    """
    import rasterio
    import numpy as np
    from scipy.ndimage import generic_filter

    filtered_value = None

    with rasterio.open(tiff_file) as dataset:
        bounds = dataset.bounds  # Get the extent (bounding box) of the raster
        if (
            bounds.left <= coordinate[1] <= bounds.right and
            bounds.bottom <= coordinate[0] <= bounds.top
        ):
            row, col = dataset.index(coordinate[1], coordinate[0])
            try:
                window = dataset.read(1, window=((row, row + window_size), (col, col + window_size))).copy()

                def lee_filter_single_pixel(w):
                    local_mean = np.mean(w)
                    local_variance = np.var(w)
                    w = w.reshape((window_size, window_size))

                    return local_mean if local_variance == 0 else (
                        w[window_size // 2, window_size // 2] * local_variance / (local_variance + 1))
                # Apply the Lee filter to the window
                filtered_value = generic_filter(window, lee_filter_single_pixel, size=window_size, mode='constant')
            except IndexError:
                pass  # Handle out-of-bounds coordinates

    return filtered_value
