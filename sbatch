#!/bin/bash

#SBATCH --time=04:59:00
#SBATCH --mem=6G
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:rtx8000:1
#SBATCH --nodes=1  # Ensure all resources are allocated on a single node

#SBATCH --output=/home/mila/c/charlie.gauthier
#SBATCH --error=/home/mila/c/charlie.gauthier

module load python/3.8
module load cuda/11.8

python3 7b.py