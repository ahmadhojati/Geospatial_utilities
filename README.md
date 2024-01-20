# Geospatial_utilities
Here I gathered a module for geospatial data processing.

# Function: `resample_and_extract_value`

Resamples a GeoTIFF image to a new resolution and extracts the pixel value at a specific coordinate.

## Parameters

- `tiff_file` (`str`): Path to the input GeoTIFF file.
- `coordinate` (`tuple`): A tuple containing latitude and longitude coordinates in decimal degrees (`lat, lon`).
- `old_resolution_meters` (`float`): The original pixel resolution in meters.
- `new_resolution_meters` (`float`): The desired new pixel resolution in meters.

## Returns

- `value` (`float or None`): The extracted pixel value at the specified coordinate in the resampled image. Returns `None` if the coordinate is out of bounds or if the extracted value is `NaN`.

# Function: `get_utm_zone`

Determines the UTM (Universal Transverse Mercator) zone number based on a given longitude.

## Parameters

- `longitude` (`float`): The longitude in decimal degrees.

## Returns

- `zone_number` (`int`): The UTM zone number corresponding to the provided longitude.

# Function: `get_epsg_code`

Computes the EPSG (European Petroleum Survey Group) code for a specific UTM zone and hemisphere.

## Parameters

- `utm_zone` (`int`): The UTM zone number.
- `hemisphere` (`str`): Hemisphere identifier (`N` for Northern or `S` for Southern).

## Returns

- `epsg_code` (`int`): The EPSG code representing the UTM zone and hemisphere combination.

# Function: `extract_values_at_coordinates`

Extracts pixel values at specified coordinates from a GeoTIFF file.

## Parameters

- `tiff_file` (`str`): Path to the input GeoTIFF file.
- `coordinate` (`tuple`): A tuple containing latitude and longitude coordinates in decimal degrees (`lat, lon`).

## Returns

- `values` (`list`): A list of extracted pixel values at the specified coordinate. The list may contain one or more values, or `None` if the coordinate is out of bounds or if values are missing.

# Function: `lee_filter`

Applies the Lee filter to a specific window in a GeoTIFF file and extracts the filtered value at a given coordinate.

The Lee filter is a speckle reduction filter used in remote sensing to enhance image quality.

## Parameters

- `window_size` (`int`): The size of the square window used for filtering. A larger window size may provide better filtering, but it can be computationally intensive.
- `tiff_file` (`str`): Path to the input GeoTIFF file.
- `coordinate` (`tuple`): A tuple containing latitude and longitude coordinates in decimal degrees (`lat, lon`).

## Returns

- `filtered_value` (`float or None`): The filtered value at the specified coordinate after applying the Lee filter. Returns `None` if the coordinate is out of bounds.
