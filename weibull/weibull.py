import numpy as np
import matplotlib.pyplot as plt
import sys
import re


usage_text = """
Usage(1): python weibull.py <function-type> <time-duration> [<parameter-set> ...]
plots weibull distribution function according to specified parameters.
function-type: `pdf' : probability density function or `cdf': cumulative distribution function.
time-duration: string formatted by t1-t2. each of t1 and t2 has to be enabled to convert to float number.
               e.g.) 0-10.0, 0-3.14, etc
parameter-set: string formatted by m,nu,gamma. each of m, nu, and gamma has to be enabled to convert to float number.
               e.g.)  3,0.5,0
               parameter-sets are enabled to specify several times. each of them corresponds to distinct plot.

Usage(2): python weibull.py [help]
prints help
"""
def pdf_weibull(t, m, nu, gamma):
    return m / (nu ** m) * ((t - gamma) ** (m - 1)) * np.exp(- ((t - gamma) / nu) ** m)


def cdf_weibull(t, m, nu, gamma):
    return 1 - np.exp(-((t - gamma) / nu) ** m)


if len(sys.argv) == 1 or sys.argv[1] == "help":
    print(usage_text)
    exit(0)

functype = sys.argv[1]
if functype != "pdf" and functype != "cdf":
    print("Invalid function type: {}".format(functype))
    exit(-1)
t1_t2 = sys.argv[2]
try:
    result = re.match(r"([0-9]+\.{0,1}[0-9]*)-([0-9]+\.{0,1}[0-9]*)", t1_t2)
    t0 = float(result.group(1))
    t1 = float(result.group(2))
except Exception as e:
    print("Invalid argument: {}".format(t1_t2))
    print(e.args)
    exit(-1)
m_list, nu_list, gamma_list = [], [], []
for i in range(len(sys.argv) - 3):
    param = sys.argv[i + 3]
    number_pattern = r"([0-9]+\.{0,1}[0-9]*),([0-9]+\.{0,1}[0-9]*),([0-9]+\.{0,1}[0-9]*)"
    try:
        result = re.match(number_pattern, param)
        m = float(result.group(1))
        nu = float(result.group(2))
        gamma = float(result.group(3))
        m_list.append(m)
        nu_list.append(nu)
        gamma_list.append(gamma)
    except Exception as e:
        print("Ignore paramter: {}".format(param))
        print(e.args)

t = np.linspace(t0, t1, 1000)
for i in range(len(m_list)):
    m = m_list[i]
    nu = nu_list[i]
    gamma = gamma_list[i]
    w = None
    if functype == "pdf":
        w = pdf_weibull(t, m, nu, gamma)
    elif functype == "cdf":
        w = cdf_weibull(t, m, nu, gamma)
    plt.plot(t, w, label="m={},nu={},gamma={}".format(m, nu, gamma))

plt.legend()
plt.show()
