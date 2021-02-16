 # EDGYBEES PROPRIETARY
 # __________________
 #
 #  [2016] - [2021] Edgy Bees Ltd and Edgy Bees Inc
 #  All Rights Reserved.
 #
 # NOTICE:  All information contained herein is, and remains
 # the property of Edgybees Inc and EdgyBees Ltd and its suppliers,
 # if any. The intellectual and technical concepts contained
 # herein are proprietary to Edgybees Inc and EdgyBees Ltd
 # and its suppliers and may be covered by U.S. and Foreign Patents,
 # patents in process, and are protected by trade secret or copyright law.
 # Dissemination of this information or reproduction of this material
 # is strictly forbidden unless prior written permission is obtained
 # from Edgybees Inc or EdgyBees Ltd
 
import math
import numpy as np
import cv2
import xml.etree.ElementTree as ET
import json
import glob
import os


def create_intrinsics_matrix(fov_h, fov_v, width, height):
    cx = width / 2
    cy = height / 2
    fx = cx / math.tan(math.radians(fov_h) / 2)
    fy = cy / math.tan(math.radians(fov_v) / 2)
    mat = np.array([fx, 0, cx, 0, fy, cy, 0, 0, 1])
    return mat.reshape(3, 3)


def rotate_around_angle(axis, angle):
    c = math.cos(math.radians(angle))
    s = math.sin(math.radians(angle))
    if axis == 'z':
        return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
    if axis == 'y':
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    if axis == 'x':
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def three_angle_rot(angles, order):
    rot_mats = [rotate_around_angle(o, a) for a, o in zip(angles, order)]
    return np.dot(rot_mats[0], np.dot(rot_mats[1], rot_mats[2]))


def kml_to_points(kml_path):
    coords = ET.parse(kml_path).getroot().findall('.//{http://www.opengis.net/kml/2.2}coordinates')
    actual_coords = []
    for coord in coords:
        coord = [float(c) for c in coord.text.strip().split(',')]
        actual_coords.append({'Latitude': coord[0], 'Longitude': coord[1], 'Altitude': coord[2]})
    return actual_coords


def meters_offset(point1, point2):
    EARTH_RADIUS = 6378137
    delta_lat = (point1['Latitude'] - point2['Latitude']) * math.pi / 180.0 * EARTH_RADIUS
    delta_long = (point1['Longitude'] - point2['Longitude']) * math.pi / 180.0 * EARTH_RADIUS * math.cos(point1['Latitude'] * math.pi / 180.0)
    return delta_long, delta_lat


def project_points(pose, terrain_altitude, points_gps, width, height):
    intrinsic_matrix = create_intrinsics_matrix(pose["Hfov"], pose["Vfov"], width, height)
    rotation_matrix = three_angle_rot([pose["Yaw"], pose["Pitch"], pose["Roll"]], ['y', 'x', 'z'])
    rotation_vector = cv2.Rodrigues(rotation_matrix.T)
    t = np.matmul(-rotation_matrix.T, [0, -(pose["Altitude"] - terrain_altitude), 0])
    gps_point = pose

    X = np.array([[meters_offset(point, gps_point)[0],
                   -(point['Altitude'] - terrain_altitude),
                   meters_offset(point, gps_point)[1]] for point in points_gps])
    projected_points = cv2.projectPoints(
        X, np.array(rotation_vector[0]), t, intrinsic_matrix, np.array([0., 0., 0., 0.]).reshape(1, 4))[0]
    return projected_points


if __name__ == '__main__':
    points = kml_to_points('samples/points.kml')
    pose = json.load(open('samples/earth_center.json'))

    for image_filename in glob.glob('samples/sandcastle/*.png'):
        print(image_filename)
        alt = int(image_filename.split('_')[1].split('.')[0])
        img = cv2.imread(image_filename)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pose['Altitude'] = alt

        # Project
        points_2d = project_points(pose, 0, points, img.shape[1], img.shape[0])

        # Draw
        color = (255, 255, 255)
        height, width, _ = img.shape
        for p in points_2d:
            cv2.circle(img, center=tuple([int(f) for f in p[0]]), radius=5, color=color, thickness=-1, lineType=8, shift=0)

        # Write text
        font = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (10, 500)
        fontScale = 1
        fontColor = (255, 255, 255)
        lineType = 2
        cv2.putText(img, str(alt),
                    bottomLeftCornerOfText,
                    font,
                    fontScale,
                    fontColor,
                    lineType)
        output_dir = 'output/sandcastle'
        os.makedirs(output_dir, exist_ok=True)
        cv2.imwrite(f'{output_dir}/{alt}.png', img)

