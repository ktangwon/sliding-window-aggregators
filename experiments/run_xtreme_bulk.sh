BULK_SIZES="1 4 16 64 256 1024 4096 16384 65536 262144 1048576 4194304 16777216 67108864 268435456"

for b in ${BULK_SIZES}; do 
    for rep in "0 1 2"; do 
        /usr/bin/time -v ../bin/bulk_evict_benchmark_driver bfinger4 geomean 1000000000 0 $b 2100000000 &>> xtreme_log.txt
    done
done
#/usr/bin/time -v ../bin/bulk_evict_benchmark_driver bfinger4 geomean 1000000000 0 268435456 2100000000
