import cProfile
import pstats
import io
from dataUncert.testDataUncert import main

pr = cProfile.Profile()
pr.enable()

for _ in range(20):
    my_result = main()

pr.disable()
s = io.StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats('tottime')
ps.print_stats()

with open('profile.txt', 'w+') as f:
    f.write(s.getvalue())
