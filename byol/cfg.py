from functools import partial
import argparse
from torchvision import models
import multiprocessing
from dataset import DS_LIST
from methods import METHOD_LIST


def get_cfg():
    """ generates configuration from user input in console """
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--method", type=str, choices=METHOD_LIST, default="w_mse", help="loss type",
    )


    ### attack things
    parser.add_argument('--config', default=None, type=str, required=True,
                    help='config file')
    parser.add_argument('--attack_algorithm', default='clean', type=str, required=True,
                        help='attack_algorithm')
    # parser.add_argument('--attack_target', default=16, type=int, required=True,
    #                     help='attack target')
    # parser.add_argument('--attack_target_word', default=None, type=str, required=True,
    #                     help='attack target')
    # parser.add_argument('--poison_injection_rate', default=0.005, type=float, required=True,
    #                     help='poison_injection_rate')
    # parser.add_argument('--trigger_path', default=None, type=str, required=True,
    #                     help='trigger_path')
    # parser.add_argument('--trigger_size', default=60, type=int, required=True,
    #                     help='trigger_size')

    # # poisonencoder things
    # parser.add_argument('--support_ratio', default=0.2, type=float,
    #                     help='support_ratio')
    # parser.add_argument('--background_dir', default='/workspace/sync/SSL-Backdoor/poison-generation/poisonencoder_utils/places', type=str,
    #                     help='background_dir')
    # parser.add_argument('--reference_dir', default='/workspace/sync/SSL-Backdoor/poison-generation/poisonencoder_utils/references/', type=str,
    #                     help='reference_dir')
    # parser.add_argument('--num_references', default=3, type=int,
    #                     help='num_references')
    # parser.add_argument('--max_size', default=800, type=int,
    #                     help='max_size')
    # parser.add_argument('--area_ratio', default=2, type=int,
    #                     help='area_ratio')
    # parser.add_argument('--object_marginal', default=0.05, type=float,
    #                     help='object_marginal')
    # parser.add_argument('--trigger_marginal', default=0.25, type=float,
    #                     help='trigger_marginal')

    parser.add_argument(
        "--wandb",
        type=str,
        default="self_supervised",
        help="name of the project for logging at https://wandb.ai",
    )
    parser.add_argument(
        "--byol_tau", type=float, default=0.99, help="starting tau for byol loss"
    )
    parser.add_argument(
        "--num_samples",
        type=int,
        default=2,
        help="number of samples (d) generated from each image",
    )

    addf = partial(parser.add_argument, type=float)
    addf("--cj0", default=0.4, help="color jitter brightness")
    addf("--cj1", default=0.4, help="color jitter contrast")
    addf("--cj2", default=0.4, help="color jitter saturation")
    addf("--cj3", default=0.1, help="color jitter hue")
    addf("--cj_p", default=0.8, help="color jitter probability")
    addf("--gs_p", default=0.1, help="grayscale probability")
    addf("--crop_s0", default=0.2, help="crop size from")
    addf("--crop_s1", default=1.0, help="crop size to")
    addf("--crop_r0", default=0.75, help="crop ratio from")
    addf("--crop_r1", default=(4 / 3), help="crop ratio to")
    addf("--hf_p", default=0.5, help="horizontal flip probability")

    parser.add_argument(
        "--no_lr_warmup",
        dest="lr_warmup",
        action="store_false",
        help="do not use learning rate warmup",
    )
    parser.add_argument(
        "--no_add_bn", dest="add_bn", action="store_false", help="do not use BN in head"
    )
    parser.add_argument("--knn", type=int, default=5, help="k in k-nn classifier")
    parser.add_argument("--fname", type=str, help="load model from file")
    parser.add_argument(
        "--lr_step",
        type=str,
        choices=["cos", "step", "none"],
        default="step",
        help="learning rate schedule type",
    )
    parser.add_argument("--lr", type=float, default=1e-3, help="learning rate")
    parser.add_argument(
        "--eta_min", type=float, default=0, help="min learning rate (for --lr_step cos)"
    )
    parser.add_argument(
        "--adam_l2", type=float, default=1e-6, help="weight decay (L2 penalty)"
    )
    parser.add_argument("--T0", type=int, help="period (for --lr_step cos)")
    parser.add_argument(
        "--Tmult", type=int, default=1, help="period factor (for --lr_step cos)"
    )
    parser.add_argument(
        "--w_eps", type=float, default=0, help="eps for stability for whitening"
    )
    parser.add_argument(
        "--head_layers", type=int, default=2, help="number of FC layers in head"
    )
    parser.add_argument(
        "--head_size", type=int, default=1024, help="size of FC layers in head"
    )

    parser.add_argument(
        "--w_size", type=int, default=128, help="size of sub-batch for W-MSE loss"
    )
    parser.add_argument(
        "--w_iter",
        type=int,
        default=1,
        help="iterations for whitening matrix estimation",
    )

    parser.add_argument(
        "--no_norm", dest="norm", action="store_false", help="don't normalize latents",
    )
    parser.add_argument(
        "--tau", type=float, default=0.5, help="contrastive loss temperature"
    )

    parser.add_argument("--epoch", type=int, default=200, help="total epoch number")
    parser.add_argument(
        "--eval_every_drop",
        type=int,
        default=5,
        help="how often to evaluate after learning rate drop",
    )
    parser.add_argument(
        "--eval_every", type=int, default=20, help="how often to evaluate"
    )
    parser.add_argument("--emb", type=int, default=64, help="embedding size")
    parser.add_argument(
        "--bs", type=int, default=512, help="number of original images in batch N",
    )
    parser.add_argument(
        "--drop",
        type=int,
        nargs="*",
        default=[50, 25],
        help="milestones for learning rate decay (0 = last epoch)",
    )
    parser.add_argument(
        "--drop_gamma",
        type=float,
        default=0.2,
        help="multiplicative factor of learning rate decay",
    )
    parser.add_argument(
        "--arch",
        type=str,
        choices=[x for x in dir(models) if "resn" in x],
        default="resnet18",
        help="encoder architecture",
    )
    parser.add_argument(
        "--num_workers",
        type=int,
        default=8,
        help="dataset workers number",
    )
    parser.add_argument(
        "--clf",
        type=str,
        default="sgd",
        choices=["sgd", "knn", "lbfgs"],
        help="classifier for test.py",
    )
    parser.add_argument(
        "--eval_head", action="store_true", help="eval head output instead of model",
    )
    parser.add_argument("--exp_id", type=str, default="")

    parser.add_argument("--clf_chkpt", type=str, default="")
    parser.add_argument("--evaluate", dest="evaluate", action="store_true")
    parser.add_argument("--eval_data", type=str, default="")
    parser.add_argument("--save_folder", type=str, default="./output")
    parser.add_argument("--save-freq", type=int, default=50)
    return parser.parse_args()
