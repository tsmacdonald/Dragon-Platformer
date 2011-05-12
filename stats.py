import pstats
stats = pstats.Stats("profile_output.cprof")
stats.print_stats()
