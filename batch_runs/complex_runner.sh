#!/bin/bash -l

declare -A el2e

el2e["La"]=3
el2e["Ce"]=4
el2e["Pr"]=5
el2e["Nd"]=6
el2e["Pm"]=7
el2e["Sm"]=8
el2e["Eu"]=9
el2e["Gd"]=10
el2e["Tb"]=11
el2e["Dy"]=12
el2e["Ho"]=13
el2e["Er"]=14
el2e["Tm"]=15
el2e["Yb"]=16
el2e["Lu"]=17

func () {
	f=$1
	base_f=$(basename $f)
	[[ ${base_f} =~ _([[:alpha:]]{2})_ ]] && lanth=${BASH_REMATCH[1]}
	[[ ${base_f} =~ (subset[[:digit:]]+)_ ]] && motif=${BASH_REMATCH[1]}
	[[ ${base_f} =~ _([[:digit:]]) ]] && oxidation=${BASH_REMATCH[1]}
	e=$((${el2e[$lanth]}-$oxidation))
	if [ $e -eq 0 ]; then
		printf "Number of active electrons is $e, skipping $f\n"	
		return
	fi	
	mkdir $cwd/motif/$motif/$lanth -p
	cp $cwd/sub.job $cwd/motif/$motif/$lanth
	cp $cwd/run.py $cwd/motif/$motif/$lanth
	cp $cwd/.pyscf_conf.py $cwd/motif/$motif/$lanth
	echo "sbatch sub.job $base_f 13 $e 0 $lanth"
	mv $f $cwd/motif/$motif/$lanth
	cd $cwd/motif/$motif/$lanth
	sbatch sub.job $base_f 13 $e 0 $lanth 
	cd $cwd
}

cwd=$(pwd)
for f in $(ls complexes_to_run)
do	
	func "complexes_to_run/$f" 
done
