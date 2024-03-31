
from flask import Flask, request, jsonify
from pydicom import dcmread
from io import BytesIO
import logging
from flask import Blueprint
from PIL import Image
import requests
import base64
import io, json
import uuid

# Create a Blueprint object
bp = Blueprint('routes', __name__)

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from app import app


# de-identify the dicom file
def deidentify_dicom(dicom_object):
    # List of sensitive data in dicom file to be de-identified and mark it as anonymous
    sensitive_data = ['PatientName', 'PatientID', 'PatientBirthDate']
    for sens_data in sensitive_data:
        if sens_data in dicom_object:
            setattr(dicom_object, sens_data, "Anonymous")
    return dicom_object

# Convet the dicom file to consistent image format
def convert_dicom_to_image(dicom_bytes, output_format='JPEG'):
    dicom_data = dcmread(BytesIO(dicom_bytes))
    pxl_data = dicom_data.pixel_array
    normalized_pxl_array = pxl_data / pxl_data.max() * 255
    image = Image.fromarray(normalized_pxl_array.astype('uint8'))
    height, width = pxl_data.shape
    with BytesIO() as output_bytes:
        image.save(output_bytes, format=output_format)
        output_bytes.seek(0)
        return output_bytes.getvalue()
    
# transfer the de-identified dicom to backend
def transmit_dicom(dicom_data, de_identified_dicom, img_cnvertd):
    dicom_data = dcmread(BytesIO(dicom_data))
    pxl_data = dicom_data.pixel_array
    normalized_pxl_array = pxl_data / pxl_data.max() * 255
    image = Image.fromarray(normalized_pxl_array.astype('uint8'))
    height, width = pxl_data.shape
    image_instance_uid = str(uuid.uuid4())
    payload = {
        "study": {
            "studyInstanceUid": de_identified_dicom.get('StudyInstanceUID', None),
            "accessionNumber": de_identified_dicom.get('AccessionNumber', None),
            "patientId": de_identified_dicom.get('PatientID', None)
        },
        "series": {
            "seriesInstanceUid":  de_identified_dicom.get('SeriesInstanceUID', None)
        },
        "images": [
            {
                "imageInstanceUid": image_instance_uid,
                "sopClassUid": de_identified_dicom.get('SOPClassUID', None),
                "height": height,
                "width": width,
                "rescaleSlope": de_identified_dicom.get('RescaleSlope', None),
                "rescaleIntercept": de_identified_dicom.get('RescaleIntercept', None),
                "photometricInterpretation": "MONOCHROME2",
                "bitsAllocated": de_identified_dicom.get('BitsAllocated', None),
                "bitsStored": de_identified_dicom.get('BitsStored', None),
                "highBit": de_identified_dicom.get('HighBit', None),
                "data": base64.b64encode(img_cnvertd).decode('utf-8')
            }
        ]
    }
    
    payload = json.dumps(payload)
    
    # Send the HTTP POST request 
    response = requests.post("https://annalise.ai/v1/images/upload", json=payload) # ---> It is throwing 404 page not upload

    # Check the response
    if response.status_code == 200:
        logger.info("DICOM file transmitted to backend successfully.")
    else:
        logger.error("Failed to transmit DICOM file. Error: %s", response.text)

@bp.route('/receive_dicom', methods=['POST'])
def index():
    try:
        dicom_data = request.data if request.data else 'sample_dicom.dcm'
        dicom_object = dcmread(BytesIO(dicom_data), force=True)
        logger.info("dicom_object: %s", dicom_object)

        de_identified_obj = deidentify_dicom(dicom_object)
        logger.info("de_identified_obj: %s", de_identified_obj)

        cnvrt_to_img = convert_dicom_to_image(dicom_data)
        
        # uncomment the below to check whether the image is converted
        # base64_image_string = base64.b64encode(cnvrt_to_img).decode('utf-8')
        # output_path = "test.jpg"
        # image_bytes = base64.b64decode(base64_image_string)
        # image = Image.open(io.BytesIO(image_bytes))
        # image.save(output_path)

        transmit_to_backend = transmit_dicom(dicom_data, de_identified_obj, cnvrt_to_img)

        return jsonify({"message": "DICOM file received successfully"}), 200

    except Exception as e:
        logger.error("An Error Occurred in DICOM file: %s", e)
        return jsonify({"error": "An Error Occurred in DICOM file"}), 500
    
if __name__ == '__main__':
    app.run(debug=True)