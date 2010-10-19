#$ -S /bin/bash
#$ -hold_jid 7250
#$ -V
#$ -cwd
#$ -j y
#$ -N cov26
#$ -o grid_output/
#$ -l h_vmem=0.5G

ARGS=`pull_args.py $*`
#SRCS0=Sun,vir,crab,cyg,cas
#SRCS1=14:11:51.20_52:13:12.2,12:57:05.53_47:18:36.2,13:38:45.77_38:55:20.7,13:31:08.57_30:29:30.2
#SRCS2=12:52:13.14_56:33:39.7,13:21:00.38_42:33:37.0,13:00:30.87_40:07:54.4,12:20:36.22_33:38:19.4,11:45:35.36_31:34:35.9,11:45:00.59_19:37:21.2,12:35:29.41_21:21:29.0,13:30:42.70_25:04:47.7
#SRCS3=13:52:19.65_31:26:44.1,15:05:27.56_26:04:59.8,14:23:20.72_19:36:10.5,11:14:11.09_40:35:01.1,12:44:20.49_16:21:42.4,12:54:14.17_27:41:40.5,14:07:08.33_34:14:36.8,14:20:54.12_41:44:18.5
SRCS0=Sun,cen
SRCS1=vir,crab,pic,hyd,for

echo cov_src26.py -C psa455_v003_gc -s ${SRCS0}/${SRCS0},${SRCS1}/${SRCS1} -b Sun,cen -c 110_400_4 -x 4 -a cross,-24 -p xx -r 15 -d 15 --maxiter=1000 $ARGS
cov_src26.py -C psa455_v003_gc -s ${SRCS0}/${SRCS0},${SRCS1}/${SRCS1} -b Sun,cen -c 110_400_4 -x 4 -a cross,-24 -p xx -r 15 -d 15 --maxiter=1000 $ARGS
