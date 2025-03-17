import os
import argparse
from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import TAGS
import exifread
from datetime import datetime

def extractFileMetadata(filePath):
    metadata = {}
    try:
        fileStat = os.stat(filePath)
        metadata["file"] = {
            "name": os.path.basename(filePath),
            "size (bytes)": fileStat.st_size,
            "created" : datetime.fromtimestamp(os.path.getctime(filePath)).strftime("%d/%m/%Y %H:%M:%S"),
            "modified": datetime.fromtimestamp(os.path.getmtime(filePath)).strftime("%d/%m/%Y %H:%M:%S")
        }
    except Exception as e:
        metadata["file_error"] = str(e)
    return metadata

def extractImgMetadata(file_path):
    metadata = {}
    try:
        with Image.open(file_path) as img:
            metadata["image"] = {
                "dimensions": f"{img.width}x{img.height}",
                "format": img.format,
                "mode": img.mode
            }
            if hasattr(img, "_getexif") and img._getexif():
                exif_data = {
                    TAGS.get(tag, tag): value
                    for tag, value in img._getexif().items()
                }
                metadata["pillow_exif"] = exif_data
    except UnidentifiedImageError as e:
        metadata["image_error"] = str(e)
    return metadata

def extractExifreadMetadata(filePath):
    metadata = {}
    with open(filePath, 'rb') as f:
        tags = exifread.process_file(f, details=False)
        if tags:
            metadata["EXIF (exifread)"] = {
                str(tag): str(value)
                for tag, value in tags.items()
                if "EXIF" in str(tag)
            }
        gps_data = {}
        if "GPS GPSLatitude" in tags and "GPS GPSLatitudeRef" in tags:
            gps_data["latitude"] = _convert_gps_coordinate(
                tags["GPS GPSLatitude"].values,
                tags["GPS GPSLatitudeRef"].values
            )
        if "GPS GPSLongitude" in tags and "GPS GPSLongitudeRef" in tags:
            gps_data["longitude"] = _convert_gps_coordinate(
            tags["GPS GPSLongitude"].values,
            tags["GPS GPSLongitudeRef"].values
            )
        if gps_data:
            metadata["GPS"] = gps_data
    return metadata

def main():
    parser = argparse.ArgumentParser(description="Metadata extractor")
    parser.add_argument("files", nargs='+')
    args = parser.parse_args()
    
    for filePath in args.files:
        if not os.path.exists(filePath):
            print(f"{filePath} not found")
            continue
        meta = extractFileMetadata(filePath)
        meta.update(extractImgMetadata(filePath))
        meta.update(extractExifreadMetadata(filePath))
        for category, data in meta.items():
            if category == "GPS":
                print("Localisation GPS:")
                print(f"  Latitude: {data.get('latitude', 'N/A')}")
                print(f"  Longitude: {data.get('longitude', 'N/A')}")
            if isinstance(data, dict):
                print(f"\n---- {category} ----")
                for key, value in data.items():
                    print(f"{key}: {value}")
        else:
            print(f"{data}")
    
    if not filePath in args.files:
        print("please provide at least a path for an image to analyze")

main()