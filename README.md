# DICOM Ingestion System Assessment

This is an Dicom Ingestion system, an assesment by annalise.ai

## Overview

This assessment involves the development of a DICOM ingestion system that redirects DICOM files from a PACS (Picture Archiving and Communication System) hosted at a customer site to a cloud-hosted backend. The system is responsible for de-identifying metadata and converting image content into a consistent format before transmission to the backend.

## Components

### Listener Component
- Listens for C-STORE requests from the PACS.
- Receives DICOM files and initiates processing.

### De-identification Component
- De-identifies sensitive metadata in DICOM files to ensure patient privacy.
- Attributes such as PatientName, PatientID, and PatientBirthDate are hided.

### Image Conversion Component
- Converts DICOM image content into a consistent format (e.g., JPEG).
- Ensures uniformity regardless of the original input format.

### Transmission to Backend
- Transmits de-identified DICOM files to the cloud-hosted backend.
- Utilizes the OpenAPI specification for defining the request payload.

## Implementation Details

### Technologies Used
- Python with Flask framework for backend development.
- PyDicom library for DICOM file manipulation.
- Pillow (PIL) for image processing tasks.
- Requests library for making HTTP requests.
- Base64 encoding for image data transmission.

### Setup Instructions
---------------
1. git clone the repository --> https://github.com/iamirfann/Dicom_Ingestion_System.git.
2. Create virtual environment using virtualenv library.
3. Inside virtual environment run pip install -r requirements.txt to install dependencies.
4. Run python app.py

### Usage
- The `/receive_dicom` endpoint is utilized for receiving DICOM files from the PACS.
- DICOM files are processed for de-identification and image conversion.
- De-identified files are transmitted to the cloud backend via a POST request.

### API Specification
- The OpenAPI specification defines the request payload expected by the backend.
- Payload includes study information, series details, and image attributes.
- Ensure compliance with the specification while transmitting DICOM data.


