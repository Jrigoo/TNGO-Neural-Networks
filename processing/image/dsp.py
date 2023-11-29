import argparse
import json
import math
import numpy as np
import sys
import io, base64
from PIL import Image

def generate_features(implementation_version, draw_graphs, raw_data, channels):
    if (implementation_version != 1):
        raise Exception('implementation_version should be 1')

    graphs = []
    all_features = []

    width = 96
    height = 96
    #raw_data = raw_data.astype(dtype=np.uint32).view(dtype=np.uint8)

    pixels_per_frame = height * width * 4
    frame_count = 0
    expected_frame_count = len(raw_data) / pixels_per_frame

    for i in np.arange(0, len(raw_data), pixels_per_frame):
        frame = raw_data[i:i+pixels_per_frame]
        bs = frame.tobytes()
        pixels = []
        frame_count = frame_count + 1
        ix = 0

        if channels == 'Grayscale':
            while ix < frame.shape[0]:
                # ITU-R 601-2 luma transform
                # see: https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.convert
                pixels.append((0.299 / 255.0) * float(bs[ix + 2]) + (0.587 / 255.0) * float(bs[ix + 1]) + (0.114 / 255.0) * float(bs[ix]))
                ix = ix + 4
        else:
            while ix < frame.shape[0]:
                pixels.append(float(bs[ix + 2]) / 255.0)
                pixels.append(float(bs[ix + 1]) / 255.0)
                pixels.append(float(bs[ix]) / 255.0)
                ix = ix + 4

        all_features = all_features + pixels

        if draw_graphs:
            im = None
            if channels == 'Grayscale':
                im = Image.fromarray(np.uint8((np.array(pixels) * 255.0).reshape(height, width)), mode='L')
            else:
                im = Image.fromarray(np.uint8((np.array(pixels) * 255.0).reshape(height, width, 3)), mode='RGB')
            im = im.convert(mode='RGBA')
            buf = io.BytesIO()
            im.save(buf, format='PNG')

            buf.seek(0)
            image = (base64.b64encode(buf.getvalue()).decode('ascii'))

            buf.close()

            name = 'Image'
            if expected_frame_count > 1:
                name = 'Frame ' + str(frame_count)

            graphs.append({
                'name': name,
                'image': image,
                'imageMimeType': 'image/png',
                'type': 'image'
            })

    num_channels = 1
    if channels == 'RGB':
        num_channels = 3

    image_config = { 'width': int(width), 'height': int(height), 'channels': num_channels, 'frames': frame_count }
    output_config = { 'type': 'image', 'shape': image_config }

    return { 'features': all_features, 'graphs': graphs, 'output_config': output_config, 'fft_used': [] }