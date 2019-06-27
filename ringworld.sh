#!/bin/bash
#SBATCH --account=def-bengioy
#SBATCH --cpus-per-task=40
#SBATCH --mem=64G
#SBATCH --time=12:0:0

module load python/3.7 scipy-stack
source ~/ENV/bin/activate
python evaluate_ringworld_baselines.py --episodes 1000000 --runtimes 40 --behavior 0.5 --target 0.4 --learner_type togtd --alpha 0.05 --beta 0.05