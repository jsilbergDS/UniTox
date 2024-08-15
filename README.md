# UniTox

UniTox is a unified dataset of 2,418 FDA-approved drugs with toxicity summaries and ratings produced by GPT-4o based on FDA drug labels for eight toxicity types: cardiotoxicity, liver toxicity, renal toxicity, pulmonary toxicity, hematological toxicity, dermatologic toxicity, ototoxicity, and infertility. The dataset is available as a CSV file in `Data/UniTox.csv`.

Please note that these toxicity ratings are produce by an AI model and should not be used in place of expert medical advice.


## GNN Training

We trained a graph neural network model called [Chemprop-RDKit](https://github.com/chemprop/chemprop) on a subset of 1,349 small molecule drugs in UniTox to predict the toxicity ratings. Commands for reproducing these results are below.

First, install the slightly modified version of Chemprop v1.6.1 that supports more flexibility in sklearn models.

```bash
conda create -y -n unitox python=3.12
conda activate unitox

git clone git@github.com:jsilbergDS/chemprop-unitox.git
git checkout v1.6.1-unitox
pip install -e .
pip install chemfunc==1.0.9
pip install numpy==1.26.1
```

**Note:** If you get the issue `ImportError: libXrender.so.1: cannot open shared object file: No such file or directory`, run `conda install -c conda-forge xorg-libxrender`.

Next, compute Morgan and RDKit fingerprints for the drugs using chemfunc version.

```bash
for FINGERPRINT_TYPE in morgan rdkit
do
chemfunc save_fingerprints \
    --data_path Data/UniTox-GNN.csv \
    --save_path Data/UniTox-GNN-${FINGERPRINT_TYPE}.npz \
    --smiles_column smiles \
    --fingerprint_type ${FINGERPRINT_TYPE}
done
```

Now, train the Chemprop models.

```bash
for SPLIT_TYPE in cv scaffold_balanced
do
for TARGET_TYPE in confident_ternary_rating_0_1 binary_rating_0_1
do
chemprop_train \
    --data_path Data/UniTox-GNN.csv \
    --dataset_type classification \
    --smiles_column smiles \
    --split_type ${SPLIT_TYPE} \
    --target_columns cardio_toxicity_${TARGET_TYPE} dermatological_toxicity_${TARGET_TYPE} hematological_${TARGET_TYPE} infertility_${TARGET_TYPE} liver_toxicity_${TARGET_TYPE} ototoxicity_${TARGET_TYPE} pulmonary_toxicity_${TARGET_TYPE} renal_toxicity_${TARGET_TYPE} \
    --show_individual_scores \
    --save_dir Models/chemprop_${TARGET_TYPE}_${SPLIT_TYPE} \
    --num_folds 10 \
    --save_preds \
    --quiet
done
done
```

Now, train the Chemprop models with fingerprints.

```bash
for SPLIT_TYPE in cv scaffold_balanced
do
for TARGET_TYPE in confident_ternary_rating_0_1 binary_rating_0_1
do
for FINGERPRINT_TYPE in morgan rdkit
do
chemprop_train \
    --data_path Data/UniTox-GNN.csv \
    --dataset_type classification \
    --smiles_column smiles \
    --features_path Data/UniTox-GNN-${FINGERPRINT_TYPE}.npz \
    --no_features_scaling \
    --split_type ${SPLIT_TYPE} \
    --target_columns cardio_toxicity_${TARGET_TYPE} dermatological_toxicity_${TARGET_TYPE} hematological_${TARGET_TYPE} infertility_${TARGET_TYPE} liver_toxicity_${TARGET_TYPE} ototoxicity_${TARGET_TYPE} pulmonary_toxicity_${TARGET_TYPE} renal_toxicity_${TARGET_TYPE} \
    --show_individual_scores \
    --save_dir Models/chemprop_${FINGERPRINT_TYPE}_${TARGET_TYPE}_${SPLIT_TYPE} \
    --num_folds 10 \
    --save_preds \
    --quiet
done
done
done
```

Now, train the MLP models.

```bash
for SPLIT_TYPE in cv scaffold_balanced
do
for TARGET_TYPE in confident_ternary_rating_0_1 binary_rating_0_1
do
for FINGERPRINT_TYPE in morgan rdkit
do
chemprop_train \
    --data_path Data/UniTox-GNN.csv \
    --dataset_type classification \
    --smiles_column smiles \
    --features_path Data/UniTox-GNN-${FINGERPRINT_TYPE}.npz \
    --no_features_scaling \
    --features_only \
    --split_type ${SPLIT_TYPE} \
    --target_columns cardio_toxicity_${TARGET_TYPE} dermatological_toxicity_${TARGET_TYPE} hematological_${TARGET_TYPE} infertility_${TARGET_TYPE} liver_toxicity_${TARGET_TYPE} ototoxicity_${TARGET_TYPE} pulmonary_toxicity_${TARGET_TYPE} renal_toxicity_${TARGET_TYPE} \
    --show_individual_scores \
    --save_dir Models/mlp_${FINGERPRINT_TYPE}_${TARGET_TYPE}_${SPLIT_TYPE} \
    --num_folds 10 \
    --save_preds \
    --quiet
done
done
done
```

Now, train random forest and SVM models on Morgan and RDKit fingerprints.

```bash
for SPLIT_TYPE in cv scaffold_balanced
do
for TARGET_TYPE in confident_ternary_rating_0_1 binary_rating_0_1
do
for FINGERPRINT_TYPE in morgan rdkit
do
for MODEL_TYPE in random_forest svm
do
sklearn_train \
    --model_type ${MODEL_TYPE} \
    --data_path Data/UniTox-GNN.csv \
    --dataset_type classification \
    --smiles_column smiles \
    --features_path Data/UniTox-GNN-${FINGERPRINT_TYPE}.npz \
    --no_features_scaling \
    --split_type ${SPLIT_TYPE} \
    --target_columns cardio_toxicity_${TARGET_TYPE} dermatological_toxicity_${TARGET_TYPE} hematological_${TARGET_TYPE} infertility_${TARGET_TYPE} liver_toxicity_${TARGET_TYPE} ototoxicity_${TARGET_TYPE} pulmonary_toxicity_${TARGET_TYPE} renal_toxicity_${TARGET_TYPE} \
    --single_task \
    --show_individual_scores \
    --save_dir Models/${MODEL_TYPE}_${FINGERPRINT_TYPE}_${TARGET_TYPE}_${SPLIT_TYPE} \
    --num_folds 10 \
    --save_preds \
    --quiet
done
done
done
done
```
