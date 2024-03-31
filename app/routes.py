
from flask import Flask, request, jsonify
from pydicom import dcmread
from io import BytesIO
import logging
from flask import Blueprint
from PIL import Image

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

@bp.route('/receive_dicom', methods=['POST'])
def index():
    try:
        dicom_data = request.data if request.data else 'sample_dicom.dcm'
        dicom_object = dcmread(BytesIO(dicom_data), force=True)
        logger.info("dicom_object: %s", dicom_object)

        de_identified_obj = deidentify_dicom(dicom_object)
        logger.info("de_identified_obj: %s", de_identified_obj)
        
        return jsonify({"message": "DICOM file received successfully"}), 200

    except Exception as e:
        logger.error("An Error Occurred in DICOM file: %s", e)
        return jsonify({"error": "An Error Occurred in DICOM file"}), 500
    
if __name__ == '__main__':
    app.run(debug=True)