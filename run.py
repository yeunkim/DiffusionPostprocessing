#!/usr/bin/python

from __future__ import print_function
import argparse
# from bids.grabbids import BIDSLayout
from functools import partial
from collections import OrderedDict
from subprocess import Popen, PIPE, check_output
import os
import subprocess
import time
import logging
import sys
import datetime

def run(command, cwd=None, stage='', filename=''):
    merged_env = os.environ
    # merged_env.update(env)
    merged_env.pop("DEBUG", None)
    logfn = stage + filename + '.log'
    logpath = os.path.join(str(cwd),'logs', logfn)
    logfile = open(logpath, 'w')
    process = Popen(command, stdout=PIPE, stderr=subprocess.STDOUT,
                    shell=True, env=merged_env, cwd=cwd)

    for line in process.stdout:
        logfile.write(line)

    while True:
        line = process.stdout.readline()
        line = str(line)[:-1]
        print(line)
        if line == '' and process.poll() != None:
            break
    if process.returncode != 0:
        raise Exception("Non zero return code: %d"%process.returncode)

def dtifit(**args):
    print(args)
    args.update(os.environ)
    cmd = 'dtifit ' + \
        '--data={data} ' + \
        '--out={out} ' + \
        '--mask={mask} ' + \
        '--bvecs={bvecs} ' + \
        '--bvals={bvals} '
    cmd = cmd.format(**args)
    print(cmd)
    t = time.time()
    logging.info(" {0} : Running DTIFIT ...".format(datetime.datetime.utcnow().strftime("%a %b %d %H:%M:%S %Z %Y")))
    logging.info(cmd)
    run(cmd, cwd=args["path"], stage='dtifit', filename='_logfile')
    elapsed = time.time() - t
    elapsed = elapsed/60
    logging.info("Finished running DTIFIT. Time duration: {0} minutes".format(str(elapsed)))

def bedpostx(**args):
    print(args)
    args.update(os.environ)
    cmd = 'bedpostx ' + \
        '{prefix}'
    cmd = cmd.format(**args)
    print(cmd)
    t = time.time()
    logging.info(" {0} : Running bedpostx ...".format(datetime.datetime.utcnow().strftime("%a %b %d %H:%M:%S %Z %Y")))
    logging.info(cmd)
    run(cmd, cwd=args["path"], stage='bedpostx', filename='_logfile')
    elapsed = time.time() - t
    elapsed = elapsed / 60
    logging.info("Finished running BedpostX. Time duration: {0} minutes".format(str(elapsed)))

def rename(**args):
    print(args)
    args.update(os.environ)
    os.rename(args["L1"], args["AD"])
    cmd = 'fslmaths ' + \
        ' {L2} -add {L3} -div 2 {RD}'
    cmd = cmd.format(**args)
    print(cmd)
    t = time.time()
    logging.info(" {0} : Renaming and creating RD ...".format(datetime.datetime.utcnow().strftime("%a %b %d %H:%M:%S %Z %Y")))
    logging.info(cmd)
    run(cmd, cwd=args["path"], stage='rename', filename='_logfile')
    elapsed = time.time() - t
    elapsed = elapsed / 60
    logging.info("Finished renaming and generating RD. Time duration: {0} minutes".format(str(elapsed)))

parser = argparse.ArgumentParser(description='Performs DTIFIT and BedpostX.')
parser.add_argument('-stage', help='Specify which stage you would like to run. '
                                   'Options: all, dtifit, bedpostx.\n'
                                   'If argument not used, default is to run both, running dtifit first.',
                    nargs='+', choices=['all', 'dtifit', 'bedpostx'], default=['all'], required=False)
parser.add_argument('-d', help='Diffusion directory that contains all the necessary files to run dtifit or bedpostx')

if len(sys.argv[1:]) ==0:
    parser.print_help()
    parser.exit()

args = parser.parse_args()
starttime = time.time()


if not os.path.exists(args.d):
    raise IOError('Path to {0} does not exist'.format(args.d))

if not os.path.exists(os.path.join(args.d, 'dti', 'logs')):
    os.makedirs(os.path.join(args.d, 'dti', 'logs'))

#set filenames
datapath = os.path.join(args.d, 'data')
dtipath = os.path.join(args.d, 'dti')

data=os.path.join(datapath, 'data.nii.gz')
out=os.path.join(args.d, 'dti', 'dti')
mask=os.path.join(datapath, 'nodif_brain_mask.nii.gz')
bvecs=os.path.join(datapath, 'bvecs')
bvals=os.path.join(datapath, 'bvals')
L1 = os.path.join(dtipath, 'dti_L1.nii.gz')
AD = os.path.join(dtipath, 'dti_AD.nii.gz')
L2 = os.path.join(dtipath, 'dti_L2.nii.gz')
L3 = os.path.join(dtipath, 'dti_L3.nii.gz')
RD = os.path.join(dtipath, 'dti_RD.nii.gz')


if 'all' in args.stage:
    # os.rename(L1, AD)
    # cmd = 'fslmaths {0} -add {1} -div 2 {2}'.format(L2, L3, RD)
    # run(cmd, cwd=args.d, stage='rename', filename='r_{0}'.format('conversion'))

    dti_stages_dict = OrderedDict( [('dtifit', partial(dtifit,
                                     path=dtipath,
                                     data=data,
                                     out=out,
                                     mask=mask,
                                     bvecs=bvecs,
                                     bvals=bvals)),
                                    ('rename', partial(rename,
                                                       path=dtipath,
                                                       L1=L1,
                                                       L2=L2,
                                                       L3=L3,
                                                       AD=AD,
                                                       RD=RD)),
                                    ('bedpostx', partial(bedpostx,
                                                         path=dtipath,
                                                         prefix=datapath))])

    for stage, stage_func in dti_stages_dict.iteritems():
        stage_func()

if args.stage and 'dtifit' in args.stage:
    dtifit_dict =  OrderedDict( [('dtifit', partial(dtifit,
                                     path=dtipath,
                                     data=data,
                                     out=out,
                                     mask=mask,
                                     bvecs=bvecs,
                                     bvals=bvals))])

    for stage, stage_func in dtifit_dict.iteritems():
        stage_func()

if args.stage and 'bedpostx' in args.stage:
    if not os.path.exists(AD) or not os.path.exists(RD):
        raise IOError('Path to AD and RD files do not exist.')

    if os.path.exists(L1) and not os.path.exists(AD):
        os.rename(L1, AD)
    elif not os.path.exists(L1) and not os.path.exists(AD):
        raise IOError('Path to {0} does not exist'.format(L1))

    if os.path.exists(L2) and os.path.exists(L3) and not os.path.exists(RD):
        cmd = 'fslmaths {0} -add {1} -div 2 {2}'.format(L2, L3, RD)
        run(cmd, cwd=dtipath, stage='rename', filename='r_{0}'.format('logfile'))
    elif not os.path.exists(L2) and not os.path.exists(L3) and not os.path.exists(RD):
        raise IOError('Path to {0} or {1} does not exist'.format(L2, L3))

    bedpostx_dict = dti_stages_dict = OrderedDict( [('bedpostx', partial(bedpostx,
                                                         path=dtipath,
                                                         prefix=datapath))])

    for stage, stage_func in bedpostx_dict.iteritems():
        stage_func()
