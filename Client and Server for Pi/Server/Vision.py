import argparse
import base64
import cv2
import os
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
import os
from PIL import Image
from PIL import ImageDraw


# [START get_vision_service]
def get_vision_service():
    print("Service Called")
    dir = os.getcwd()
    print(dir)
    API_KEY = 'XXXX'
    return discovery.build('vision', 'v1', developerKey=API_KEY)
# [END get_vision_service]


def detect_face(face_file, max_results=4):

    """Uses the Vision API to detect faces in the given file.
    Args:
        face_file: A file-like object containing an image with faces.
    Returns:
        An array of dicts with information about the faces in the picture.
    """
    print("Vision API - detect_face() Called")
    image_content = face_file.read()
    batch_request = [{
        'image': {
            'content': base64.b64encode(image_content).decode('utf-8')
            },
        'features': [{
            'type': 'FACE_DETECTION',
            'maxResults': max_results,
            }]
        }]

    service = get_vision_service()
    request = service.images().annotate(body={
        'requests': batch_request,
        })
    response = request.execute()

    return response['responses'][0]['faceAnnotations']


def highlight_faces(image, faces, output_filename):
    """Draws a polygon around the faces, then saves to output_filename.
    Args:
      image: a file containing the image with the faces.
      faces: a list of faces found in the file. This should be in the format
          returned by the Vision API.
      output_filename: the name of the image file to be created, where the
          faces have polygons drawn around them.
    """
    print("Vision API - highlight_faces() Called")
    im = Image.open(image)
    draw = ImageDraw.Draw(im)

    for face in faces:
        box = [(v.get('x', 0.0), v.get('y', 0.0))
               for v in face['fdBoundingPoly']['vertices']]
        draw.line(box + [box[0]], width=5, fill='#00ff00')

    im.save(output_filename)


def main(input_filename, output_filename, max_results):
    print("Vision API - main() Called")
    with open(input_filename, 'rb') as image:
        print("Calling Vision API - detect_face()")
        faces = detect_face(image, max_results)
        print('Found {} face{}'.format(
            len(faces), '' if len(faces) == 1 else 's'))

        print('Writing to file {}'.format(output_filename))
        # Reset the file pointer, so we can read the file again
        image.seek(0)
        print("Calling Vision API - highlight_faces()")
        highlight_faces(image, faces, output_filename)
        return faces