set term wxt persist size 1440,900
set multiplot layout 1,2
set title "AFL++ scaling in fork and persist modes"
set xlabel "Number of cores"
set ylabel "Fuzz cases per second (total)"
set grid xtics ytics mxtics mytics
set logscale y
plot "afl_fork.txt" u 1:2 w l t "Fork Mode", "afl_persist.txt" u 1:2 w l t "Persist Mode", "afl_shared_memory_persist.txt" u 1:2 w l t "AFL Shared Memory Persist Mode"

set ylabel "Fuzz cases per second per core"
plot "afl_fork.txt" u 1:($2 / $1) w l t "Fork Mode", "afl_persist.txt" u 1:($2 / $1) w l t "Persist Mode", "afl_shared_memory_persist.txt" u 1:($2 / $1) w l t "AFL Shared Memory Persist Mode"

