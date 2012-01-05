import pstats

#Used for profiling
stats = pstats.Stats("profile_output.cprof")
stats.print_stats()
