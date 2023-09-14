"""
# estimate sample size via power analysis
from statsmodels.stats.power import TTestIndPower
# parameters for power analysis
effect = 0.2
alpha = 0.05
power = 0.8
nobs = 40
# perform power analysis
analysis = TTestIndPower()
result = analysis.solve_power(effect_size=None, power=power, nobs1=nobs, ratio=1.0, alpha=alpha)
print('Effect Size: %.3f' % result)
"""

# estimate sample size via power analysis
from statsmodels.stats.power import TTestIndPower
from statsmodels.stats.power import FTestAnovaPower
# parameters for power analysis
effect = 0.5
alpha = 0.05
nobs = 32
# perform power analysis
analysis = FTestAnovaPower()
result = analysis.solve_power(effect_size=effect, power=None, nobs=nobs, k_groups=2, alpha=alpha)
print(result)

# parameters for power analysis
power = 0.8
alpha = 0.05
nobs = 32
# perform power analysis
analysis = FTestAnovaPower()
result = analysis.solve_power(effect_size=None, power=power, nobs=nobs, k_groups=2, alpha=alpha)
print(result)

