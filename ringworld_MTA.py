from utils import *
from methods import *
from greedy import *
from MTA import *
import numpy as np
import numpy.matlib as npm
import warnings, argparse, scipy.io

parser = argparse.ArgumentParser(description='')
parser.add_argument('--alpha', type=float, default=0.05, help='')
parser.add_argument('--beta', type=float, default=0.05, help='')
parser.add_argument('--kappa', type=float, default=0.01, help='')
parser.add_argument('--episodes', type=int, default=100000, help='')
parser.add_argument('--runtimes', type=int, default=16, help='')
parser.add_argument('--N', type=int, default=11, help='')
parser.add_argument('--target', type=float, default=0.4, help='')
parser.add_argument('--behavior', type=float, default=0.5, help='')
parser.add_argument('--comparison', type=int, default=0, help='')
args = parser.parse_args()

# experiment Preparation
N = args.N; env, runtimes, episodes, gamma = RingWorldEnv(args.N, unit = 1), args.runtimes, args.episodes, lambda x: 0.95
alpha, beta, kappa = args.alpha, args.beta, args.kappa
target_policy = npm.repmat(np.array([args.target, 1 - args.target]).reshape(1, -1), env.observation_space.n, 1)
behavior_policy = npm.repmat(np.array([args.behavior, 1 - args.behavior]).reshape(1, -1), env.observation_space.n, 1)

# get ground truth expectation, variance and stationary distribution
true_expectation, true_variance, stationary_dist = iterative_policy_evaluation(env, target_policy, gamma=gamma)
evaluate = lambda estimate, stat_type: evaluate_estimate(estimate, true_expectation, true_variance, stationary_dist, stat_type)
things_to_save = {}

error_value_mta = eval_MTA(env, true_expectation, true_variance, stationary_dist, behavior_policy, target_policy, kappa=kappa, gamma=gamma, alpha=alpha, beta=beta, runtimes=runtimes, episodes=episodes, evaluate=evaluate)
things_to_save['error_value_mta_mean'], things_to_save['error_value_mta_std'] = np.nanmean(error_value_mta, axis=0), np.nanstd(error_value_mta, axis=0)

if args.comparison:
    BASELINE_LAMBDAS = [0, 0.2, 0.4, 0.6, 0.8, 1]
    for baseline_lambda in BASELINE_LAMBDAS:
        Lambda = LAMBDA(env, lambda_type = 'constant', initial_value = baseline_lambda * np.ones(N))
        results = eval_togtd(env, true_expectation, stationary_dist, behavior_policy, target_policy, Lambda, gamma = gamma, alpha=alpha, beta=beta, runtimes=runtimes, episodes=episodes, evaluation = evaluation)
        exec("things_to_save[\'error_value_togtd_%g\'] = results.copy()" % (baseline_lambda * 1e5))
    error_value_greedy, lambda_greedy, error_var_greedy = eval_greedy(env, true_expectation, true_variance, stationary_dist, behavior_policy, target_policy, gamma = gamma, alpha=alpha, beta=beta, runtimes=runtimes, episodes=episodes, evaluation = evaluation)
    things_to_save['error_value_greedy'], things_to_save['lambda_greedy'], things_to_save['error_var_greedy'] = error_value_greedy, lambda_greedy, error_var_greedy

filename = 'ringworld_N_%s_behavior_%g_target_%g_episodes_%g_kappa_%g' % (N, behavior_policy[0, 0], target_policy[0, 0], episodes, kappa)
scipy.io.savemat(filename, things_to_save)
pass