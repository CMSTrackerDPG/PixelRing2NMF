# Development of Pixel Ring 1 and 2 NFM

Made by J. Morris and A. Lapertosa (Summer 2025).

Inspired by [NFM applied to Pixel Barrel by L. Lambrecht](https://github.com/LukaLambrecht/pixelae/tree/main/studies/pixel_clusters_2024) (Spring 2025).

In these folders, there are the files needed to train and test the NMF model for Ring 1-2 cluster position on 2024-25 data.

## data

ZeroBias*.parquet files (heavy, not loaded on GitHub).

Original files produced by Luka stored at: /eos/user/l/llambrec/dialstools-output/

## excels

Final tables with list of anomalies found on 2024-25 data.

Note: Ring 1 (valid for 2024 data only), Ring 2 (until 2025F)

## Links.md

Talks and references related to TkDQM and ML in general.

## models

Model files in .pkl format, .png of components in subfolder

## notebooks

Notebooks and needed libraries (functions, nmf2d, plottools, skip_kernel_extension)

### Train_model.ipynb

Train model on specific run:

1) General imports
2.1) Import .parquet file (data) and .json file (DCS flags from OMS)
2.2) Define run to be used for training (exclude LS with anomalies)
3) Data pre-processing (remove cross)
4) Train them model
5) Save the model (and .png of components)

### Apply_model_to_era.ipynb

Test the model to specific era:

0) General imports and variable definition
1) Load the appropriate model
2) Import runs and check LS that pass the DCS flags
3) Predict
4) Loop over each run (store predictions)
5) Calculate the losses and binary losses
6) Analyze the anomalies
7) Identify Anomaly Types
8) Merge Excel files for whole Ring
9) Save specific LS in .png plot (Data, Predictions, Losses, and Binary Losses)

## omsdata

Files in .json format (DCS flags from OMS).

Original files produced by Luka available here: https://github.com/LukaLambrecht/pixelae/tree/main/studies/pixel_clusters_2024/omsdata

## results

Folders with results:
- .xlsx with anomalies in each run
- Predictions.npy is too heavy (Gb), not saved on GitHub
