# Deploying a SKLearn NMF model

The following instructions explains how to prepare a SKLearn based model to be deployed in DIALS. The example model prepared do not have a dynamic threshold built-in, so the Metric Key (`output_1`) will be used in DIALS with a threshold stored in the DIALS database and editable via the User Interface.

## Requirements

1. **Make sure you have run the [`fetch_METSig_data.ipynb`](fetch_METSig_data.ipynb) notebook beforehand to cache the data required to train and evaluate the model.**

## Steps

1. **Train and export the model**  
   Run the [`main.ipynb`](main.ipynb) notebook to:  
   - Define the model  
   - Train the model  
   - Export the model in the `ubj` format

2. **Build the template**  
   ```bash
   dismcli build -f template.yaml
   ```  
   After a successful validation, the built SKLearn model will be available in the `.dism-artifacts` directory, along with the updated `template.yaml`.  

   > **Note:** You do **not** need to manually update these files.  

   Optionally, you can validate your template against the development instance of DIALS:  
   ```bash
   dismcli build -f template.yaml -u https://dev-cmsdials-api.web.cern.ch
   ```

3. **(Optional) Test the model in a container**  
   Ensure Docker is installed, then run:  
   ```bash
   dismcli start-api -r NMFRegressor
   ```

   If everything works as expected, the api will be accessible locally and you can test the predictions using the script [`test_predictions.py`](scripts/test_predictions.py).
   ```bash
   python test_predictions.py -r 360950 -n metsig-nmf-regressor -p 8080
   ```

4. **Package the model**  
   ```bash
   dismcli package
   ```  
   This generates the final `template.yaml` inside `.dism-artifacts/package`.  

   Optionally, use the development instance of DIALS:  
   ```bash
   dismcli package -u https://dev-cmsdials-api.web.cern.ch
   ```

5. **Request model registration**  
   - [Open an issue](https://gitlab.cern.ch/cms-ppd/technical-support/web-services/dials-service/-/issues/new) in the **dials-service** repository with the title:  
     ```
     [Request] Model registration
     ```  
   - In the issue body:  
     - Describe your request  
     - Attach the packaged template:  
       ```
       .dism-artifacts/package/template.yaml
       ```  
   - Wait for a DIALS maintainer to handle the registration.  
   - If there’s a problem with the model, discussion will take place in the same issue.  
   - After successful registration, the model is **not** automatically marked as `active` — you must activate it manually via the UI.
