for file in $1/*
do 
	for file2 in $2/*
	do
		echo "comparing $file and $file2" 
		python text-matcher.py "$file" "$file2" > kjv-books-experiment.txt
	done
done
