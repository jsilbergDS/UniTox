# UniTox

UniTox is a unified dataset of 2,418 FDA-approved drugs with toxicity summaries and ratings produced by GPT-4o based on FDA drug labels for eight toxicity types: cardiotoxicity, liver toxicity, renal toxicity, pulmonary toxicity, hematological toxicity, dermatologic toxicity, ototoxicity, and infertility. The dataset is available as a CSV file in `Data/UniTox.csv`.

Please note that these toxicity ratings are produce by an AI model and should not be used in place of expert medical advice.


## GNN Training

We trained a graph neural network model called [Chemprop-RDKit](https://github.com/chemprop/chemprop) on a subset of 1,349 small molecule drugs in UniTox to predict the toxicity ratings. Commands for reproducing these results are below.

First, compute RDKit fingerprints for the drugs using chemfunc version 1.0.4.

```bash
chemfunc save_fingerprints \
    --data_path Data/UniTox-GNN.csv \
    --save_path Data/UniTox-GNN.npz
```

Now, train the Chemprop-RDKit model (Chemprop version 1.6.1) in four settings: (random [cv] or scaffold split) x (ternary or binary rating).

```bash
for SPLIT_TYPE in cv scaffold_balanced
do
for TARGET_TYPE in confident_ternary_rating_0_1 binary_rating_0_1
do
chemprop_train \
    --data_path Data/UniTox-GNN.csv \
    --dataset_type classification \
    --smiles_column smiles \
    --features_path Data/UniTox-GNN.npz \
    --no_features_scaling \
    --split_type ${SPLIT_TYPE} \
    --target_columns cardio_toxicity_${TARGET_TYPE} dermatological_toxicity_${TARGET_TYPE} hematological_${TARGET_TYPE} infertility_${TARGET_TYPE} liver_toxicity_${TARGET_TYPE} ototoxicity_${TARGET_TYPE} pulmonary_toxicity_${TARGET_TYPE} renal_toxicity_${TARGET_TYPE} \
    --show_individual_scores \
    --save_dir Models/chemprop_rdkit_${TARGET_TYPE}_${SPLIT_TYPE} \
    --num_folds 10 \
    --quiet
done
done
```

Now, train random forest and SVM models on Morgan fingerprints or Morgan fingerprints + RDKit descriptors.

```bash
for SPLIT_TYPE in cv scaffold_balanced
do
for TARGET_TYPE in confident_ternary_rating_0_1 binary_rating_0_1
do
for MODEL_TYPE in random_forest svm
do
for FEATURES_TYPE in morgan morgan_rdkit
do

if [ "$FEATURES_TYPE" = "morgan_rdkit" ]; then
    FEATURES_STRING="--features_path Data/UniTox-GNN.npz"
else
    FEATURES_STRING=""
fi

sklearn_train \
    --model_type ${MODEL_TYPE} \
    --data_path Data/UniTox-GNN.csv \
    --dataset_type classification \
    --smiles_column smiles \
    --no_features_scaling ${FEATURES_STRING} \
    --split_type ${SPLIT_TYPE} \
    --target_columns cardio_toxicity_${TARGET_TYPE} dermatological_toxicity_${TARGET_TYPE} hematological_${TARGET_TYPE} infertility_${TARGET_TYPE} liver_toxicity_${TARGET_TYPE} ototoxicity_${TARGET_TYPE} pulmonary_toxicity_${TARGET_TYPE} renal_toxicity_${TARGET_TYPE} \
    --single_task \
    --show_individual_scores \
    --save_dir Models/${MODEL_TYPE}_${FEATURES_TYPE}_${TARGET_TYPE}_${SPLIT_TYPE} \
    --num_folds 10 \
    --quiet
done
done
done
done
```
