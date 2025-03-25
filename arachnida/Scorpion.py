import os
import argparse
from PIL import Image, ExifTags, UnidentifiedImageError
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

def convertCoordinate(values, ref):
    degrees = float(values[0].num) / values[0].den
    minutes = float(values[1].num) / values[1].den
    seconds = float(values[2].num) / values[2].den
    
    decimal = degrees + (minutes / 60) + (seconds / 3600)
    
    direction = ref.values if isinstance(ref, exifread.utils.Ratio) else ref
    if direction in ['S', 'W']:
        decimal = -decimal
    
    return round(decimal, 6)

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
        gpsData = {}
        if "GPS GPSLatitude" in tags and "GPS GPSLatitudeRef" in tags:
            gpsData["latitude"] = convertCoordinate(tags["GPS GPSLatitude"].values, tags["GPS GPSLatitudeRef"].values)
        if "GPS GPSLongitude" in tags and "GPS GPSLongitudeRef" in tags:
            gpsData["longitude"] = convertCoordinate(tags["GPS GPSLongitude"].values,tags["GPS GPSLongitudeRef"].values)
        if gpsData:
            metadata["GPS"] = gpsData
    return metadata

def deleteMetadata(path):
    img = Image.open(path)
    data = list(img.getdata())
    img = Image.new(img.mode, img.size)
    img = Image.new(img.mode, img.size)
    img.putdata(data)
    img.save(path)
    print(f"Metadata deleted for {path}")


def main():
    parser = argparse.ArgumentParser(description="Metadata extractor")
    parser.add_argument("files", nargs='+')
    parser.add_argument("-d", "--delete", action="store_true")
    args = parser.parse_args()
    
    for filePath in args.files:
        if not os.path.exists(filePath):
            print(f"{filePath} not found")
            continue
        if not args.delete:
            meta = extractFileMetadata(filePath)
            meta.update(extractImgMetadata(filePath))
            meta.update(extractExifreadMetadata(filePath))
            for category, data in meta.items():
                if isinstance(data, dict):
                    print(f"\n---- {category} ----\n")
                    for key, value in data.items():
                        print(f"{key}: {value}")
                else:
                    print(f"{data}")

        else:
            deleteMetadata(filePath)
    
    if not filePath in args.files:
        print("please provide at least a path for an image to analyze")

main()