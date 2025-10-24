# Deployment of Pixel Ring 2 NMF

Made by A. Lapertosa (Autumn 2025).

Inspired by [ML4DQM meeting talks](https://indico.cern.ch/event/1593463/) and [DISM tutorial](https://gitlab.cern.ch/cms-ppd/technical-support/tools/dism-examples/).

Deployed on October 2025:
- GitHub issue: https://gitlab.cern.ch/cms-ppd/technical-support/web-services/dials-service/-/issues/139
- Model 17 (active): https://dev-cmsdials.web.cern.ch/models/17?ws=global
- Valid for 2024 and 2025 data (since run 382800, era 2024F) 

## mlserver-model

Folder with all libraries needed for the ML Server:
- app.py: interface between central DIALS syntax and custom model syntax
- bad_ROC.py: search for anomalies (input: loss map, output: True flag if Multi-Disk anomaly is found in the LS)
- datatype.py: data type definitions
- dftools.py: panda dataframe functions (import data, filter on DCS flags)
- functions.py: Ring 1-2 specific (identify power group, define anomaly type, plotting)
- nmf2d.py: general NMF definitions
- omstools.py: OMS functions (find OMS indices and attributes)
- pixelring2nmf.joblib: model saved in .joblib format
- pixelring2nmf.py: model application steps (pre-process, infer, predict, loss, flag, filter, de-process...)
- preprocessor.py: pre-processing (add and remove the cross)

## Other files

Other files needed for running on local or on ML server:
- omsid.py: credentials to retrieve data from OMS
- template.yaml: general definitions of the model
- test_data.pkl: file not saved on GitHub (see step 2.1)
- template_packaged_model_7_2024-25.yaml: file used to [request model Deployment (GitLab issue 139)](https://gitlab.cern.ch/cms-ppd/technical-support/web-services/dials-service/-/issues/139)
- test_predictions.py: used to test the model on ML server (see step 2.)

## 1. How to test the model on SWAN

1) Save test_data.pkl 
2) Execute the test, running the model on SWAN

**Expected output** (in case of 1 LS with Multi-Disk anomaly)

[INFO]: Flagging results (before filtering): flagged 1 out of 750 lumisections. 
[INFO]: Filtering: selected 750 out of 750 lumisections. 
[INFO]: Flagging results (after filtering): flagged 1 out of 750 lumisections. 

### 1.1 Save_Test_Data_pickle.ipynb

Steps:
- Import data (Ring 2 data from DIALS in .parquet, DMS flags from OMS in .json).
- Select a specific run (i.e. batch of 750 LS) in the era .parquet
- Attach DCS flags
- Save as test_data.pkl used as input data for testing

### 1.2 Test_Ring2_model_outsideMLServer.ipynb

Steps:
- Import model (.pkl from Development/models folder)
- Import data (test_data.pkl generated before)
- Test the model
- Save the model in .joblib format

## 2. How to test the model on ML server on Linux

### 2.1 Enter in Linux environment

Note: Lxplus is problematic... Use local linux (Virtual Machine or Windows Subsystem for Linux)

### 2.2 Make sure python3.11 is installed
```
python --version 
```
--> Python 3.11.0rc1 

### 2.3 Install DISM
```
pip install "cmsdism[docker,podman]" 
```

### 2.4 Download MLServer docker image (5 Gb)

```
docker pull seldonio/mlserver:1.5.0 
```

### 2.5 Save link to image with proper name 

```
docker tag seldonio/mlserver:1.5.0 registry.cern.ch/docker.io/seldonio/mlserver:1.5.0
```

### 2.6 Check docker images

```
docker images 
```

### 2.7 Enter python ven

```
python -m venv .venv 
source .venv/bin/activate 
```

### 2.8 Build the template

Use ""-u ...dev-cmsdials" to validate on the development instance of DIALS.

```
dismcli build -f template.yaml -u https://dev-cmsdials-api.web.cern.ch 
```

**Expected output:**
INFO: Device authorized, authentication finished successfully! 
INFO: Building resource (PixelRing2NMF, InferenceService::MLServer::SKLearn) 

Note: After a successful validation, the built SKLearn model will be available in the `.dism-artifacts` directory, along with the updated `template.yaml`.

### 2.9 Launch API (the server)

```
dismcli start-api -r PixelRing2NMF 
```

**Expected output:**
[mlserver][pixel-ring2-nmf:0.1.0] INFO - Loaded model 'pixel-ring2-nmf' successfully. 

### 2.10 Open another terminal

### 2.11 Test the model

```
python test_predictions.py -n pixel-ring2-nmf -p 8080 
```

**Expected output (on the second terminal):**

Number of LS: 750 
Number of flagged LS: 1 
 
**Expected output (on the first terminal):**

[INFO]: Flagging results (before filtering): flagged 1 out of 750 lumisections. 
[INFO]: Filtering: selected 468 out of 750 lumisections. 
[INFO]: Flagging results (after filtering): flagged 1 out of 750 lumisections. 

INFO:     172.17.0.1:58898 - "POST /v2/models/pixel-ring2-nmf/infer HTTP/1.1" 200 OK 

## 3. Package the model

Use ""-u ...dev-cmsdials" to validate on the development instance of DIALS.

```bash
dismcli package -u https://dev-cmsdials-api.web.cern.ch 
```  

Note: This generates the final `template.yaml` inside `.dism-artifacts/package`.

## 4. Request model registration

Steps:
- [Open an issue](https://gitlab.cern.ch/cms-ppd/technical-support/web-services/dials-service/-/issues/new) in the **dials-service** repository with title "[Request] Model registration"
- Describe the model and other details
- Attach the packaged template:
```
.dism-artifacts/package/template.yaml
```  

## 5. Enjoy