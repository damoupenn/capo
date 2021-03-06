#$ -S /bin/bash
#$ -j y
#$-o grid_output
ARGS=`pull_args.py $*`
CORRECT=correct_pgb015.py
CAL=pgb015_v006
#ANTS="cross,-16,-31,-3_13,-3_14,-3_29,-4_14,-4_15,-4_30,-4_32,-5_15,-5_32,-6_32,-13_20,-14_21,-15_21,-15_22,-15_23,-20_29,-21_30,-21_32,-22_32,-23_32"
ANTS="cross,-1"

SRCS=Sun
SRCS1="cas,cyg,crab,vir,Sun"

for FILE in $ARGS; do
    $CORRECT $FILE -t /data1/paper/arp/pgb015/temps
    apply_bp.py ${FILE}c #--scale=.0000000816326
    xrfi.py -c 0_239,720_1023 -m val ${FILE}cb
    tempgain.py ${FILE}cbr --gom=1
    filter_src.py -C $CAL -s $SRCS -d 3 --clean=1e-4 ${FILE}cbrt
    #combine_freqs.py -n 256 ${FILE} #cbr
    ###############combine_files.py -n 4 --nfiles=12 ${FILE} #cbrm
    #/data1/paper/arp/scripts/cov_src26.py -d 10 -r 15 -C $CAL -s $SRCS1 -c 80_180 -x 4 -a $ANTS -p xx --maxiter=1000 ${FILE} #cbrmM
    #/data1/paper/arp/scripts/rm_npz26.py ${FILE} -d 10 -r 15 -C $CAL -D .
    #xtalk3.py ${FILE}d #cbrmMd
    #correct_filename.py ${FILE} #cbrmMdx
done
