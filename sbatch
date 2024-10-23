#!/bin/bash

#SBATCH --time=04:59:00
#SBATCH --mem=31G
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:a100l:1
#SBATCH --nodes=1  # Ensure all resources are allocated on a single node
#SBATCH --output=/home/mila/c/charlie.gauthier/olmo-server/logs/out_%A_%a.log

module load python/3.8
module load cuda/11.8

export HF_HOME='/network/scratch/c/charlie.gauthier/hfcache'

python3 1.py