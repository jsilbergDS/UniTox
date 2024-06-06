# UniTox


## GNN Training

First, compute RDKit fingerprints for the drugs using chemfunc version 1.0.4.

```bash
chemfunc save_fingerprints \
    --data_path Data/UniTox-GNN.csv \
    --save_path Data/UniTox-GNN.npz
```

Now, train the Chemprop-RDKit model in four settings: (random (cv) or scaffold split) x (ternary or binary rating).

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
    --target_columns cardio_toxicity_${TARGET_TYPE} dermatologic_toxicity_${TARGET_TYPE} hematotoxicity_${TARGET_TYPE} infertility_${TARGET_TYPE} liver_toxicity_${TARGET_TYPE} ototoxicity_${TARGET_TYPE} pulmonary_toxicity_${TARGET_TYPE} renal_toxicity_${TARGET_TYPE} \
    --show_individual_scores \
    --save_dir Models/chemprop_rdkit_${TARGET_TYPE}_${SPLIT_TYPE} \
    --num_folds 10 \
    --quiet
done
done
```
